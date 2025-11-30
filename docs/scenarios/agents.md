# Scenarios

## GitHub リポジトリで管理されるファイルを参照するエージェント

### GitHub の Personal Access Token の作成

GitHub の `Developer Settings > Personal access tokens` でパーソナルアクセストークンを作成し、以下のスコープを付与します。
今回は特定のリポジトリのファイルを参照するため、Fine-grained tokens を選択し、対象リポジトリに対して Permission として `Contents` の `Read-only` を付与します。

### Microsoft Foundry で GitHub MCP Tool を作成

Microsoft Foundry ポータルから Tools タブを開き、`Connect a tool` をクリックします。
Catalog から `GitHub MCP Tool` を選択し、作成した Personal Access Token を指定してツールを作成します。

### エージェントの作成

Microsoft Foundry ポータルから Agents タブを開き、`Create agent` をクリックします。
Agent 作成画面で `Tools` セクションを開き、先ほど作成した GitHub MCP Tool をエージェントに追加します。

## カスタム MCP Tool を使用するエージェント

### カスタム MCP Tool の作成

[ks6088ts/template-mcp-python](https://hub.docker.com/repository/docker/ks6088ts/template-mcp-python/general) にある Docker イメージを使用して、カスタム MCP Tool を作成し、エージェントに追加します。
例えば、Azure Container Apps で `ks6088ts/template-mcp-python:latest` イメージを使用してコンテナをデプロイし、MCP Tool として登録します。Ingress の設定で外部からアクセス可能にすることを忘れないでください。
また、環境変数として `MCP_HOST`, `MCP_PORT` を設定し、外部からアクセスできるようにします。

### エージェントの作成

Microsoft Foundry ポータルから Agents タブを開き、`Create agent` をクリックします。
Agent 作成画面で `Tools` セクションを開き、先ほど作成したカスタム MCP Tool をエージェントに追加します。
