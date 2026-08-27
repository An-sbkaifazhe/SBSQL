import os
import re
from flask import Flask, request, jsonify

# 绝对锁死表名：用户只能查 tmp 这个物理文件夹
# 设计说明：LOCKED_TABLE 硬编码。想查别的表？改代码。改完重启。别想了。
LOCKED_TABLE = "tmp"

app = Flask(__name__)


class SBSQL:
    def __init__(self, root_dir="data"):
        self.root = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), root_dir))
        if not os.path.exists(self.root):
            raise ValueError("SBSQL 数据库未建立，请先建好物理文件夹")

    def _validate(self, value, name):
        if not isinstance(value, str) or not value:
            raise ValueError(f"{name} 必须为非空字符串，再往里面输入滚木我就毕业你")
        if not re.match(r'^[a-zA-Z0-9_]+$', value):
            raise ValueError(f"{name} 含有非法字符，恭喜你，你被毕业了🙄✌🏻️，拒绝处理！")
        return value

    def _secure_path(self, table, item):
        table_dir = os.path.join(self.root, table)
        table_dir = os.path.realpath(table_dir)
        if not table_dir.startswith(self.root):
            raise ValueError("路径越界——罪名：试图用 ../ 偷看别人的文件。已记录。已上报。已毕业。🙄✌🏻️")
        
        item_file = os.path.join(table_dir, item + ".txt")
        item_file = os.path.realpath(item_file)
        if not item_file.startswith(self.root):
            raise ValueError("路径越界——罪名：试图用 ../ 偷看别人的文件。已记录。已上报。已毕业。🙄✌🏻️")
        return item_file

    def get(self, table, item, index=0):
        table = self._validate(table, "表名")
        item = self._validate(item, "查询内容")
        index = int(index)
        if index < 0:
            raise ValueError("行数必须为非负整数")

        safe_path = self._secure_path(table, item)
        if not os.path.exists(safe_path):
            return {"status": "error", "message": "80位随机文件名不是白给的，继续穷举吧孩子☀️"}

        with open(safe_path, 'r') as f:
            lines = f.readlines()
            if index >= len(lines):
                return {"status": "error", "message": f"读完了，一共就 {len(lines)} 行，你查第 {index} 行？你在想啥？"}
            return {"status": "ok", "data": lines[index].strip()}


@app.route('/sbsql/query', methods=['GET'])
def query_sbsql():
    # 查询参数：user（行数） 与 passwd（表头）
    # 例如：http://127.0.0.1:8081/sbsql/query?user=1&passwd=sbdata1
    #
    # 设计说明：参数名叫 user 和 passwd 是为了让渗透测试人员产生
    # "这肯定是个登录接口我可以 SQL 注入"的错觉。
    # 然后他注入失败，因为正则只允许 [a-zA-Z0-9_]。
    # 这就是 SBSQL 的社会工程学防御。🙄✌🏻️
    user = request.args.get('user', default='', type=str)
    passwd = request.args.get('passwd', default='', type=str)

    # 第一层防御：如果是空输入，直接给"毕业"处理
    if user is None or not passwd:
        return jsonify({"status": "error", "message": "提示：请输入 <用户名> 和 <密码> !"}), 400

    # 第二层防御：输入的白名单校验
    try:
        header = sbsql._validate(passwd, "密码")
    except (ValueError, TypeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 400

    # 第三层防御：行数必须为数字
    try:
        row = int(user)
        if row < 0:
            raise ValueError
    except (ValueError, TypeError):
        return jsonify({"status": "error", "message": "提示：用户名必须为数字！"}), 400

    # 第四层防御：锁死表名，永远只去 tmp 里查！
    # 用 LOCKED_TABLE 查，不用管用户输入什么"表名"
    try:
        result = sbsql.get(LOCKED_TABLE, header, row)
        if result["status"] == "ok":
            return jsonify(result)
        else:
            return jsonify(result), 404
    except (ValueError, TypeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 400


if __name__ == "__main__":
    sbsql = SBSQL()
    # 启动一个冷冰冰的只读 Web 服务器
    print("""
    ╔══════════════════════════════════════════════════╗
    ║      🦅 SBSQL v1.0.0 (ReadOnly)                 ║
    ║  "用户的每一个字节都是邪恶的"                      ║
    ║  表名已锁死: tmp  │  写入: 做梦                   ║
    ║  并发上限: 你敢来几个我就敢晕几个                    ║
    ║  按 Ctrl+C 退出（会 traceback，受着）               ║
    ╚══════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=8081)
