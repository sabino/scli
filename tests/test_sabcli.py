import subprocess

def test_echo():
    result = subprocess.run(['python', '-m', 'sabcli', 'echo', 'Hello, World!'], capture_output=True, text=True)
    assert result.stdout.strip() == 'Hello, World!'

def test_echo_reverse():
    result = subprocess.run(['python', '-m', 'sabcli', 'echo', 'Hello, World!', '--reverse'], capture_output=True, text=True)
    assert result.stdout.strip() == '!dlroW ,olleH'
