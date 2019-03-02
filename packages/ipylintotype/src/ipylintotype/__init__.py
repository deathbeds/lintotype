def _jupyter_server_extension_paths():
    return [{
        "module": "ipylintotype"
    }]

def load_jupyter_server_extension(nbapp):
    nbapp.log.info("ipylintotype")
