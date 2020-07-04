import os
import time
import subprocess
import platform
import shutil
import secrets
from threading import Thread


def main():

    home = os.path.expanduser('~')
    if not os.path.exists(f"{home}/.ssh/id_rsa"):
        os.system('ssh-keygen -b 2048 -t rsa -f ~/.ssh/id_rsa -q -N ""')

    port = 8080
    cs_instance = Thread(target=run_code_server, args=[port])
    http_server_instance = Thread(target=http_server)

    if os.path.exists(cs_log):
        os.remove(cs_log)

    passwd = secrets.token_hex(10)
    os.environ['PASSWORD'] = passwd

    subprocess.Popen(
        'code-server --bind-addr localhost:8080 > /dev/null',
        shell=True)

    http_server_instance.start()
    cs_instance.start()

    wait(f'not os.path.exists("{cs_log}")', 20)
    wait(f'os.path.getsize("{cs_log}") < 400', 20)
    wait(f'not os.path.exists("{h_log}")', 20)
    wait(f'os.path.getsize("{h_log}") < 400', 20)

    cs_url = open(cs_log, 'r').read()

    for line in cs_url.splitlines():
        if 'url=' in line:
            cs_url = line[line.rindex('=') + 1::]

    http_url = open(h_log, 'r').read()

    for line in http_url.splitlines():
        if 'url=' in line:
            http_url = line[line.rindex('=') + 1::]

    html = '<!DOCTYPE html>\n<html>\n\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\n<style>\n\nbody {\n  display:flex; flex-direction:column; justify-content:center;\n  min-height:90vh;\n}\n\nhtml {\n  background-color: black;\n}\n\ndiv {\n  text-align: center;\n  background-color: white;\n  width: 50%;\n  border: 15px solid #02D2CC;\n  padding: 50px;\n  margin: auto;\n  \n  \n  border-bottom-right-radius:5%;\n  border-bottom-left-radius:5%;\n  border-top-right-radius:5%;\n  border-top-left-radius:5%;\n}\n\ninput {\n\ttext-align: center;\n    font-size: 1em;\n}\n\nbutton {\n  background-color: #5DE525;\n  border-bottom-right-radius:20%;\n  border-bottom-left-radius:20%;\n  border-top-right-radius:20%;\n  border-top-left-radius:20%;\n}\n\n\n</style>\n\n<body>\n\n<div>\n\t<input id="txt" value="' + \
        passwd + '" style="border:none; fon" readonly/> <br>\n    <a href=\'' + cs_url + '\' target="_blank">سرور</a> <br>\n    <button id="btn" style="border:none">کپی رمز</button >\n</div>\n\n\n\n<script> \nconst txt = document.querySelector(\'#txt\')\nconst btn = document.querySelector(\'#btn\')\n\nconst copy = (text) => {\n  const textarea = document.createElement(\'textarea\')\n  document.body.appendChild(textarea)\n  textarea.value = text\n  textarea.select()\n  document.execCommand(\'copy\')\n  textarea.remove()\n}\n\nbtn.addEventListener(\'click\', (e) => {\n  copy(txt.value)\n})\n</script>\n\n</body>\n</html>\n\n\n'

    htf = open('html/index.html', 'w')
    htf.write(html)
    htf.close()

    print("url:", http_url)

    while True:
        time.sleep(320)


def wait(condition, seconds):
    counter = 0

    while eval(condition):
        if counter > seconds:
            raise Exception

        time.sleep(1)
        counter += 1


def run_code_server(port):
    cmd = f"ngrok http {cs_port} --log=stdout > {cs_log}"
    subprocess.check_output(cmd, shell=True)


def http_server():
    subprocess.Popen(
        f"ngrok http {http_port} --log=stdout > {h_log}",
        shell=True)
    os.system(
        f"python3 -m http.server {http_port} -d html > /dev/null"
    )


if __name__ == '__main__':

    OS = platform.uname().system
    if OS not in ["Linux", "Darwin"]:
        raise Exception("Not supported")

    cs_log = "ngrok.log"
    h_log = "ngrok2.log"
    ngrok = "ngrok-stable-linux-amd64.zip"
    ngrok_release = "https://bin.equinox.io/c/4VmDzA7iaHb/"
    cs = "code-server-3.4.1-linux-amd64.tar.gz"
    cs_release = "https://github.com/cdr/code-server/releases/download/3.4.1/"
    cbin = "code-server/bin"
    http_port = 3030
    cs_port = 8080

    os.makedirs("html", exist_ok=True)

    if OS == 'Darwin':
        ngrok = "ngrok-stable-darwin-amd64.zip"
        cs = "code-server-3.4.1-macos-amd64.tar.gz"

    cs_release += cs
    ngrok_release += ngrok

    if not os.path.exists('code-server'):
        subprocess.call(['curl', '-L', cs_release, '-o', cs])
        subprocess.call(['tar', '-xvf', cs])
        subprocess.call(['mv', '.'.join(cs.split('.')[0:3]), 'code-server'])
        os.remove(cs)

    os.environ['PATH'] += f':{cbin}'

    if shutil.which('ngrok') is None:

        if not os.path.exists(f'{cbin}/ngrok'):
            subprocess.call(['curl', ngrok_release, '-o', ngrok])
            subprocess.call(['unzip', '-d', cbin, ngrok])
            os.remove(ngrok)

        os.chmod(f'{cbin}/ngrok', 0o775)

    try:
        main()
    except Exception as e:
        print(f"Could not establish connection: {e}")
