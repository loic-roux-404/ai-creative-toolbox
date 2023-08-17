from gradio_client import Client


def recognize(url):
    client = Client("https://doctrp.docscanner.top/", verbose=False)
    result = client.predict(url, api_name="/predict")
    return result
