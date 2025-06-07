
def build_cmd(roomname, config):
    room_id = config['ROOMBA_ROOM_MAPPINGS'][roomname]
    cmd = "{\"command\": \"start\", \"ordered\": 1, \"pmap_id\": \"y8EXMLHpSIid-FGLMHXzIQ\",\"regions\": [{ \"region_id\": \"<room_id>\", \"type\": \"rid\" }], \"user_pmapv_id\": \"221025T055042\"}"
    cmd = cmd.replace('<room_id>', room_id)
    return cmd
    

def clean_wilmas_room():
    return {
         "cmd": {
                    "command": "start",
                    "ordered": 1,
                    "pmap_id": "h2XNg54oQfSFoEuhlJunGA",
                    "regions": [
                        {
                            "region_id": "2",
                            "type": "rid"
                        }
                    ],
                    "user_pmapv_id": "220218T123722"
                }
    }