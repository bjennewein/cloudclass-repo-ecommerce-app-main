from flask import Flask, request, Response
import requests

load_balancer = Flask(__name__, static_folder=None)

targets = [
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
]

current_index = 0


@load_balancer.route("/", defaults={"path": ""}, methods=["GET", "POST"])
@load_balancer.route("/<path:path>", methods=["GET", "POST"])
def balance(path):
    global current_index

    target = targets[current_index]
    current_index = (current_index + 1) % len(targets)

    target_url = f"{target}/{path}"

    response = requests.request(
        method=request.method,
        url=target_url,
        params=request.args,
        data=request.get_data(),
        headers={
            key: value
            for key, value in request.headers
            if key.lower() != "host"
        },
        cookies=request.cookies,
        allow_redirects=False,
    )

    excluded_headers = {
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    }

    headers = [
        (key, value)
        for key, value in response.headers.items()
        if key.lower() not in excluded_headers
    ]

    return Response(
        response.content,
        status=response.status_code,
        headers=headers,
    )


if __name__ == "__main__":
    load_balancer.run(
        host="127.0.0.1",
        port=8000,
        debug=False,
    )