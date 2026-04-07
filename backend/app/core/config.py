from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Azure OpenAI
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = "gpt-4o"
    azure_openai_api_version: str = "2024-12-01-preview"

    # Azure Cosmos DB
    cosmos_endpoint: str = "https://localhost:8081"
    cosmos_key: str = ""
    cosmos_database: str = "contract-intelligence"

    # Azure AI Document Intelligence
    doc_intelligence_endpoint: str = ""
    doc_intelligence_key: str = ""

    # Azure Blob Storage
    blob_connection_string: str = ""
    blob_container_name: str = "contracts"

    # Local development fallbacks
    use_local_storage: bool = True
    use_local_parser: bool = True

    # CUAD dataset path (relative to backend/)
    cuad_data_path: str = "data"

    # Server
    app_host: str = "0.0.0.0"
    app_port: int = 8000
