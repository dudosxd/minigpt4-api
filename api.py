import websockets
import json
import secrets
import base64

async def gradioWs(url,session_hash,input,update,fn):
    
    output = {}
    input['session_hash'] = session_hash
    input['fn_index'] = fn
    
    async with websockets.connect(url) as websocket:
        try:
            while True:
                data = json.loads(await websocket.recv())
                
                # отправляем хэш в ответ на запрос на отправку хэша
                if data['msg'] == "send_hash":
                    hash = json.dumps({"session_hash":session_hash,"fn_index":fn})
                    await websocket.send(hash)
                
                if data['msg'] == "estimation":
                    update(f'{data["rank"]}/{data["queue_size"]} {data["rank_eta"]}')
                
                elif data['msg'] == "send_data":
                    await websocket.send(json.dumps(input))

                elif data['msg'] == "process_starts":
                    update("[+] Generating")

                elif data['msg'] == "process_completed":
                    update("[+] Generated")
                    output = data
                            
        except websockets.exceptions.ConnectionClosedOK:
            update("The server closed the connection")
            return output
        
class MiniGPT4:
    def __init__(self,servPath,imagePath) -> None:
            
        with open(imagePath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())

        self.img = ("data:image/jpeg;base64," + encoded_string.decode("utf-8"))
        self.serv = servPath
        self.session_hash = secrets.token_hex(16)    
        self.data = []
        
        self.isfirst = True
        
    async def load(self,log):
        data = {"data":[self.img,"",None]}
        out = await gradioWs(self.serv,self.session_hash,data,log,0)
        return out
        
    async def __fask__(self,prompt,log):
        data1 = {"data":[prompt,[],None]}
        out1 = await gradioWs(self.serv,self.session_hash,data1,log,1)
        data2 = {"data":[out1['output']['data'][1],None,None,1,1]}
        out2 = await gradioWs(self.serv,self.session_hash,data2,log,2)
        self.data = out2
        self.isfirst = False
        return out2
        
    async def __ask__(self,prompt,log):
        data1 = {"data":[prompt,self.data['output']['data'][0],None]}
        out1 = await gradioWs(self.serv,self.session_hash,data1,log,1)
        
        data2 = {"data":[out1['output']['data'][1],None,None,1,1]}
        out2 = await gradioWs(self.serv,self.session_hash,data2,log,2)
        self.data = out2
        return out2
    
    async def ask(self,prompt,log):
        if self.isfirst:return await self.__fask__(prompt,log)
        else:return await self.__ask__(prompt,log)
    
