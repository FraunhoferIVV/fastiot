from fastiot.core.app import FastIoTApp

app = FastIoTApp()

@app.loop(inject=)
async def produce():
    pass
