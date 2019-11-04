import asyncio
import websockets
import logging

class XVIZServer:
    def __init__(self, handlers, port=3000, per_message_deflate=True):
        '''
        :param handlers: single or list of handlers that acts as function and return a session object, or None if not supported
        '''
        if not handlers:
            raise ValueError("No handler is registered!")
        elif not isinstance(handlers, (list, tuple)):
            self._handlers = [handlers]
        else:
            self._handlers = handlers

        self._logger = logging.getLogger("xviz-server")

        compression = "deflate" if per_message_deflate else None
        self._server_loop = websockets.serve(self.handle_session, "localhost", port,
                                             compression=compression)

    async def handle_session(self, socket, request):
        '''
        This function handles all generated connection
        '''
        self._logger.info("[> Connection] created.")
        if "?" in request:
            path, params = request.split("?")
        else:
            path, params = request, ""
        params = [item.split("=") for item in params.split("&") if "=" in item]
        params = {k:v for k, v in params}
        params['path'] = path

        # find proper handler
        for handler in self._handlers:
            session = await handler(socket, params)
            if session:
                session.on_connect()
                return

        socket.close()
        self._logger.info("[> Connection] closed due to no handler found")

    def start(self):
        asyncio.get_event_loop().run_until_complete(self._server_loop)
        asyncio.get_event_loop().run_forever()
