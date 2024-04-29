# 配置环境变量；如果您已经提前将api-key提前配置到您的运行环境中，可以省略这个步骤
import os
os.environ['DASHSCOPE_API_KEY']='sk-d0e5d832a6e8429284a683aa0f8b5668'
os.environ['AMAP_TOKEN']='b10bff0a2fa86f53ec9aebae92b84b27'

# 选用RolePlay 配置agent
from modelscope_agent.agents.role_play import RolePlay  # NOQA
from modelscope_agent.tools.base import BaseTool
from modelscope_agent.tools import register_tool
import pandas as pd
from numpy import dtype


@register_tool('create_python_file')
class create_python_file(BaseTool):
    description = '在本地创建一个 Python 文件'
    name = 'create_python_file'
    parameters: list = [{
        'name': 'file_path',
        'description': 'Python 文件本地路径',
        'required': True,
        'type': 'string'
    }, {
        'name': 'file_content',
        'description': 'Python 文件内容',
        'required': True,
        'type': 'string'
    }]

    def call(self, params: str, **kwargs):
        params = self._verify_args(params)
        file_path = params['file_path']
        file_content = params['file_content']

        # 检查文件路径是否正确
        if not file_path.endswith('.py'):
            return str({'result': '文件路径不是 Python 文件 (.py)'})

        try:
            with open(file_path, 'w') as file:
                file.write(file_content)
            return str({'result': f'成功创建 Python 文件, 文件路径为 {file_path}'})
        except Exception as e:
            return str({'result': f'创建文件时发生错误: {e}'})

@register_tool('read_python_files')
class read_python_files(BaseTool):
    description = '读取本地文件夹中的所有 Python 文件'
    name = 'read_python_files'
    parameters: list = [{
        'name': 'folder_path',
        'description': '本地文件夹路径',
        'required': True,
        'type': 'string'
    }]

    def call(self, params: str, **kwargs):
        params = self._verify_args(params)
        folder_path = params['folder_path']

        # 检查文件夹路径是否存在
        if not os.path.exists(folder_path):
            return str({'result': '文件夹路径不存在'})
        if not os.path.isdir(folder_path):
            return str({'result': '给定的路径不是一个文件夹'})

        try:
            # 初始化一个空列表来存储文件内容
            file_contents = {}
            for filename in os.listdir(folder_path):
                if filename.endswith('.py'):
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r') as file:
                        code = file.read()
                    file_contents[filename] = code
            return str({'result': f'成功读取 Python 文件, 文件内容为 {file_contents}'})
        except Exception as e:
            return str({'result': f'读取文件时发生错误: {e}'})




@register_tool('save_python_files')
class SavePythonFile(BaseTool):
    description = '保存Python文件到指定路径'
    name = 'Save_python_file'
    parameters: list = [{
        'name': 'file_content',
        'description': 'Python文件的内容',
        'required': True,
        'type': 'string'
    },
        {
            'name': 'save_path',
            'description': '保存路径',
            'required': True,
            'type': 'string'
        }]

    def call(self, params: str, **kwargs):
        params = self._verify_args(params)
        file_content = params['file_content']
        save_path = params['save_path']

        # 确保保存路径的目录存在
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # 将内容写入文件
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(file_content)

        return str({'result': f'Python文件已保存至{save_path}'})


role_template = '你扮演一个程序员，请根据要求完成任务。'
llm_config = {'model': 'glm-4', 'model_server': 'zhipu'}
function_list = ['code_interpreter', 'create_python_file', 'read_python_files', 'save_python_files']
bot = RolePlay(
   function_list=function_list, llm=llm_config, instruction=role_template)


# 用于存储对话历史记录的列表
dialog_history = []

def main():
    while True:
        try:
            # 获取用户输入
            user_input = input("请输入您的问题（输入'退出'来结束程序）: ")
            if user_input.lower() == '退出':
                print("程序已退出。")
                break

            # 将用户的问题追加到对话历史记录中
            dialog_history.append(user_input)

            # 使用bot处理用户输入的问题，并将对话历史作为上下文传递给模型
            response = bot.run("\n".join(dialog_history))

            # 输出答案
            text = ''
            for chunk in response:
                text += chunk
            print(text)

            # 将答案追加到对话历史记录中
            dialog_history.append(text)

        except KeyboardInterrupt:
            # 如果用户按下Ctrl+C，则退出程序
            print("\n程序已退出。")
            break
        except Exception as e:
            # 打印错误信息并继续
            print(f"发生错误：{e}", file=sys.stderr)
            continue


if __name__ == "__main__":
    main()