import base64
import chainlit as cl
import requests
import openai
from agents import Agent, Runner
from agents.tracing.setup import TraceProvider
from agents.model_settings import ModelSettings
from agents.mcp.util import MCPUtil
from agents.mcp.server import MCPServer, MCPServerSse

from chainlit.input_widget import McpServerInput, Slider, TextInput

AUTH_URL = "http://personal_secretary_devcontainer-personal_ai_secretary-1:8100/api/v1/auth/token2"  # FastAPI認証API



async def parse_mcp_server_settings(settings):
    """
    Parse the MCP server settings from the user input.
    """
    
    # string[]を分解
    # URL, mcp_path, auth_path, username, passwordを分解
    url, mcp_path, auth_path, username, password = settings
    return url, mcp_path, auth_path, username, password

async def connect_mcp_server():

    # ユーザー情報の取得
    user = cl.user_session.get("user")
    if not user:
        await cl.Message("ユーザー情報が見つかりません。").send()
        await cl.stop()
        return

    await cl.Message(f"✅ ようこそ、{user.identifier} さん！").send()

    # ユーザのMCPサーバから取得したトークンを保持する
    token = user.metadata.get("token")

    # ここでMCPサーバにトークンを渡すなどの処理を行う
    mcp_server = MCPServerSse(
        name="Test MCP Server",
        params={
            "url": "http://personal_secretary_devcontainer-personal_ai_secretary-1:8100/mcp",
            "headers": {
                "Authorization": f"Bearer {token}",  # トークンをヘッダーに追加
            }
        },
    )
    await mcp_server.connect()
    cl.user_session.set("mcp_server", mcp_server)

    # OpenAI Agent SDKの初期化
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    cl.user_session.set("agent", agent)




@cl.on_chat_start
async def on_chat_start():
    # 最初の一言を表示
    await cl.Message("こんにちは。今日は何をお手伝いしましょうか？まずはチャットのセッティングをしてください。").send()
    #
    # Chat settings
    #
    settings = await cl.ChatSettings(
        [
            McpServerInput(
                id="mcp_server_settings",
                label="MCP Server",
                initial=["http://personal_secretary_devcontainer-personal_ai_secretary-1:8100", "/mcp", "/api/v1/auth/token2", "hirokazu", "kizuna"],
            )
        ]
    ).send()    

    # ユーザーセッションからMCPサーバの設定を取得
    cl.user_session.set("mcp_server_settings", settings["mcp_server_settings"])

    # ユーザーセッションの初期化
    cl.user_session.set("mcp_server", None)

    # チャット履歴の初期化    
    cl.user_session.set("chat_history", [])

@cl.on_settings_update
async def on_settings_update(settings):
    """
    Handle settings update event.
    """
    # Sending an action button within a chatbot message
    actions = [
        cl.Action(name="action_button", payload={"value": "example_value"}, label="接続する", )
    ]

    await cl.Message(content="MCPサーバと接続しますか？", actions=actions).send()

import chainlit as cl

@cl.action_callback("action_button")
async def on_action(action):
    await cl.Message(content=f"MCPサーバへの接続を行いました。").send()
    # Optionally remove the action button from the chatbot user interface
    """
    Set up the agent with the selected settings.
    """
    params = cl.user_session.get("mcp_server_settings")
    
    # ユーザーセッションからMCPサーバの設定を取得
    url, mcp_path, auth_path, username, password = await parse_mcp_server_settings(params)

    try:
        auth_url = url + auth_path
        res = requests.post(
            auth_url,
            json={"username": username, "password": password},
            timeout=5
        )
        res.raise_for_status()
        token = res.json()["access_token"]

        cl.user_session.set("token", token)        
    except Exception as e:
        print(f"Auth failed: {e}")
        return None  # 認証失敗

    # MCPServerSseの初期化
    mcp_url = url + mcp_path
    mcp_server = MCPServerSse(
        name="Test MCP Server",
        params={
            "url": mcp_url,
            "headers": {
                "Authorization": f"Bearer {cl.user_session.get('token')}",  # トークンをヘッダーに追加
            }
        },
    )
    
    # ユーザーセッションに保存
    await mcp_server.connect()
    cl.user_session.set("mcp_server", mcp_server)
    await cl.Message("MCPサーバへの接続に成功しました。").send()

    # OpenAI Agent SDKの初期化
    agent = Agent(
        name="Assistant",
        instructions="Use the tools to answer the questions.",
        mcp_servers=[mcp_server],
        model_settings=ModelSettings(tool_choice="required"),
    )

    cl.user_session.set("agent", agent)
    await cl.Message("AIエージェントに接続しました。").send()


    await action.remove()



@cl.on_message
async def on_message(message: cl.Message):
    print(f"Received message: {message.content}")
    #AIエージェントにメッセージを構築する
    ai_message = {"role": "user", "content": [
            {
                "type": "input_text",
                "text": message.content,
            }
        ]}
    
    data = None
    if message.elements:
        for element in message.elements:
            if element.type == "file":
                file_path = element.path  # ← ファイルの一時保存パス
                file_name = element.name

                # 任意の処理：例としてファイルを読み込む
                data = None
                with open(file_path, "rb") as f:
                    data = f.read()

                await cl.Message(f"受け取ったファイル名: {file_name}").send()
            elif element.type == "image":
                file_path = element.path  # ← ファイルの一時保存パス
                file_name = element.name

                # 画像種別を判定する
                if file_name.endswith(".png"):
                    image_type = "image/png"
                elif file_name.endswith(".jpg") or file_name.endswith(".jpeg"):
                    image_type = "image/jpeg"
                else:
                    image_type = "image/jpeg"

                # 任意の処理：例としてファイルを読み込む
                data = None
                with open(file_path, "rb") as f:
                    data = f.read()
                    # 画像をBase64エンコード
                    if data:
                        image64 = base64.b64encode(data).decode('utf-8')
                        print(f"Image64 (first 100 chars): {image64[:100]}")  # 先頭100文字のみ表示

                        ai_message["content"].append({
                            "type": "input_image",
                            "image_url": f"data:{image_type};base64,{image64}"
                        })

                await cl.Message(f"受け取ったファイル名: {file_name}").send()                
            else:
                print(f"Unknown element type: {element.type}")




    #print(f"AI message: {ai_message}")
    # チャット履歴の取得と更新
    history = cl.user_session.get("chat_history")
    history.append(ai_message)

    # AI Agentを取得
    agent: Agent = cl.user_session.get("agent")
    if not agent:
        await cl.Message("AI Agentが初期化されていません。").send()
        return

    try:
        # ユーザーからのメッセージをエージェントに送信    
        result = await Runner.run(starting_agent=agent, input=history)
        raw_responses = result.raw_responses
        print(f"Raw responses: {raw_responses}")
        output = result.final_output
        
        # ツール実行結果をGPT-4oに送り返して続きの回答
        history.append({
            "role": "assistant",
            "content": output,
        })
        
        await cl.Message(output).send()

    except Exception as e:
            await cl.Message(f"⚠️ エラーが発生しました: {str(e)}").send()
    except Exception as e:
            # 401などトークン期限切れを検出
            if "401" in str(e) or "Unauthorized" in str(e):
                await cl.Message("🔐 セッションが切れました。再ログインします...").send()


