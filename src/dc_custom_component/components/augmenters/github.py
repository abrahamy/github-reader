import io
from pathlib import Path
from uuid import uuid4
from zipfile import ZipFile

from haystack import Document, component
from haystack.utils import Secret
from httpx import Client, HTTPError


class GitHubError(RuntimeError):
    pass


class APIError(GitHubError):
    pass


class RepositoryNameError(GitHubError):
    pass


@component
class GitHubRepositoryReader:
    """Retrieve the files in a GitHub repository and return a list of documents"""

    def __init__(
        self,
        access_token: Secret,
        repository: str,
        file_extensions: list[str],
        file_encoding: str = "utf-8",
        ref: str = "main",
    ) -> None:
        """Initializes the component.

        :param access_token: GitHub API access token
        :param repository: GitHub repository name in the form "owner/repo"
        :param file_extensions: File extensions
        :param file_encoding: The default file encoding for reading the files in the repository, defaults to "utf-8"
        :param ref: The branch or tag to read from, defaults to "main"
        :raises RepositoryNameError: Raised when the repository name is invalid.
        """
        self.ref = ref
        self.encoding = file_encoding
        self.file_extensions = file_extensions

        self.access_token = access_token

        try:
            self.owner, self.repo = repository.split("/")
        except ValueError as ex:
            raise RepositoryNameError(
                f"Please specify a valid repository name in the form `owner/repo` instead of {repository!r}."
            ) from ex

        self.http_client = Client(
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {self.access_token.resolve_value()}",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            follow_redirects=True,
        )

    @component.output_types(documents=list[Document])
    def run(self, repository: str | None = None, ref: str | None = None) -> dict[str, list[Document]]:
        ref = ref or self.ref
        owner, repo = self.owner, self.repo

        if repository:
            try:
                owner, repo = repository.split("/")
            except ValueError as ex:
                raise RepositoryNameError(
                    f"Please specify a valid repository name in the form `owner/repo` instead of {repository!r}."
                ) from ex

        endpoint_url = f"https://api.github.com/repos/{owner}/{repo}/zipball/{ref}"

        return {"documents": self._github_repo_to_docs(endpoint_url)}

    def _github_repo_to_docs(self, endpoint_url: str) -> list[Document]:
        try:
            response = self.http_client.get(endpoint_url)
            response.raise_for_status()
        except HTTPError as ex:
            raise APIError(f"Failed to download repository content (url: {endpoint_url}). Reason: {ex!s}.") from ex

        documents = []

        with ZipFile(io.BytesIO(response.read())) as archive:
            for filename in archive.namelist():
                file_path = Path(filename)

                if file_path.suffix not in self.file_extensions:
                    continue

                file_id = str(uuid4())

                doc = Document(
                    id=file_id,
                    content=archive.read(filename).decode(self.encoding),
                    meta={
                        "file_id": file_id,
                        "file_name": file_path.name,
                        "file_path": filename,
                    },
                )

                documents.append(doc)

        return documents
