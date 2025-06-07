'''
Created on 18 feb. 2017

@author: davandev
'''
import requests
import logging
import os

global logger
logger = logging.getLogger(os.path.basename(__file__))

XML_START_TAG ="""<?xml version="1.0" encoding="utf-8" standalone="yes"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body>"""
XML_END_TAG = """</s:Body></s:Envelope>"""

#replace_queue_tag ="""<u:ReplaceQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueContext>&lt;?xml version=&quot;1.0&quot; ?&gt;&lt;PlayList&gt;&lt;ListName&gt;davanserver_tts_service&lt;/ListName&gt;&lt;ListInfo&gt;&lt;Radio&gt;0&lt;/Radio&gt; &lt;SourceName&gt;davanserver_tts_service&lt;/SourceName&gt;&lt;TrackNumber&gt;2&lt;/TrackNumber&gt;&lt;SearchUrl&gt;&lt;/SearchUrl&gt;&lt;Quality&gt;2&lt;Quality&gt;&lt;/ListInfo&gt;&lt;Tracks&gt;&lt;Track1&gt;&lt;Source&gt;davanserver_tts_service1&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/mp3=announcement.mp3&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service1&lt;/Source&gt;&lt;Id&gt;0&lt;/Id&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;202135&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=announcement.mp3&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Over the Horizon1&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;Samsung&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;Brand Music&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track1&gt;&lt;Track2&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Id&gt;1&lt;/Id&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;1&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;202135&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Over the Horizon&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;Samsung&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;Brand Music&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track2&gt;&lt;/Tracks&gt;&lt;/PlayList&gt;</QueueContext></u:ReplaceQueue>"""
#replace_queue_tag ="""<u:ReplaceQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueContext>&lt;?xml version=&quot;1.0&quot; ?&gt;&lt;PlayList&gt;&lt;ListName&gt;davanserver_tts_service&lt;/ListName&gt;&lt;ListInfo&gt;&lt;Radio&gt;0&lt;/Radio&gt; &lt;SourceName&gt;davanserver_tts_service&lt;/SourceName&gt;&lt;TrackNumber&gt;2&lt;/TrackNumber&gt;&lt;SearchUrl&gt;&lt;/SearchUrl&gt;&lt;Quality&gt;2&lt;Quality&gt;&lt;/ListInfo&gt;&lt;Tracks&gt;&lt;Track1&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/mp3=announcement.mp3&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Id&gt;0&lt;/Id&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;202135&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=announcement.mp3&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Over the Horizon&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;Samsung&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;Brand Music&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track1&gt;&lt;Track2&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Id&gt;0&lt;/Id&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;202135&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Over the Horizon&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;Samsung&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;Brand Music&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track2&gt;&lt;/Tracks&gt;&lt;/PlayList&gt;</QueueContext></u:ReplaceQueue>"""
replace_queue_tag = """<u:ReplaceQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueContext>&lt;?xml version=&quot;1.0&quot; ?&gt;&lt;PlayList&gt;&lt;ListName&gt;davanserver_tts_service&lt;/ListName&gt;&lt;ListInfo&gt;&lt;Radio&gt;0&lt;/Radio&gt;&lt;SourceName&gt;davanserver_tts_service&lt;/SourceName&gt;&lt;TrackNumber&gt;1&lt;/TrackNumber&gt;&lt;SearchUrl&gt;&lt;/SearchUrl&gt;&lt;Quality&gt;2&lt;/Quality&gt;&lt;/ListInfo&gt;&lt;Tracks&gt;&lt;Track1&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Id&gt;0&lt;/Id&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;202135&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Over the Horizon&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;Samsung&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;Brand Music&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track1&gt;&lt;/Tracks&gt;&lt;/PlayList&gt;</QueueContext></u:ReplaceQueue>"""
CREATE_QUEUE_TAG = """<u:CreateQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueContext>&lt;?xml version=&quot;1.0&quot; ?&gt;&lt;PlayList&gt;&lt;ListName&gt;davanserver_tts_service&lt;/ListName&gt;&lt;ListInfo&gt;&lt;Radio&gt;0&lt;/Radio&gt;&lt;SourceName&gt;davanserver_tts_service&lt;/SourceName&gt;&lt;TrackNumber&gt;1&lt;/TrackNumber&gt;&lt;SearchUrl&gt;&lt;/SearchUrl&gt;&lt;Quality&gt;2&lt;/Quality&gt;&lt;RealIndex&gt;4&lt;/RealIndex&gt;&lt;/ListInfo&gt;&lt;Tracks&gt;&lt;Track1&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/testb-mp3&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;1071&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Hangouts Message&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;&amp;amp;lt;unknown&amp;amp;gt;&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;Notifications&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track1&gt;&lt;/Tracks&gt;&lt;/PlayList&gt;</QueueContext></u:CreateQueue>"""
APPEND_TRACK_IN_QUEUE = """<u:AppendTracksInQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueContext>&lt;?xml version=&quot;1.0&quot; ?&gt;&lt;PlayList&gt;&lt;ListName&gt;davanserver_tts_service&lt;/ListName&gt;&lt;ListInfo&gt;&lt;Radio&gt;0&lt;/Radio&gt;&lt;SourceName&gt;davanserver_tts_service&lt;/SourceName&gt;&lt;TrackNumber&gt;1&lt;/TrackNumber&gt;&lt;SearchUrl&gt;&lt;/SearchUrl&gt;&lt;Quality&gt;2&lt;/Quality&gt;&lt;RealIndex&gt;4&lt;/RealIndex&gt;&lt;/ListInfo&gt;&lt;Tracks&gt;&lt;Track1&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Id&gt;0&lt;/Id&gt;&lt;Key&gt;http://so.ard.iyyin.com/s/song_with_out?q=Emergency_20170115_215820%20%3Cunknown%3E&amp;amp;size=50&amp;amp;page=1&lt;/Key&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;5480&amp;quot;&amp;gt;http://192.168.2.44:8080/mp3=<replace_with_mp3_file>&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Emergency_20170115_215820&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;&amp;amp;lt;unknown&amp;amp;gt;&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;&amp;amp;lt;unknown&amp;amp;gt;&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track1&gt;&lt;/Tracks&gt;&lt;/PlayList&gt;</QueueContext></u:AppendTracksInQueue>"""
APPEND_EXT_TRACK_IN_QUEUE = """<u:AppendTracksInQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueContext>&lt;?xml version=&quot;1.0&quot; ?&gt;&lt;PlayList&gt;&lt;ListName&gt;davanserver_tts_service&lt;/ListName&gt;&lt;ListInfo&gt;&lt;Radio&gt;0&lt;/Radio&gt;&lt;SourceName&gt;davanserver_tts_service&lt;/SourceName&gt;&lt;TrackNumber&gt;1&lt;/TrackNumber&gt;&lt;SearchUrl&gt;&lt;/SearchUrl&gt;&lt;Quality&gt;2&lt;/Quality&gt;&lt;RealIndex&gt;4&lt;/RealIndex&gt;&lt;/ListInfo&gt;&lt;Tracks&gt;&lt;Track1&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;URL&gt;<replace_with_mp3_file>&lt;/URL&gt;&lt;Source&gt;davanserver_tts_service&lt;/Source&gt;&lt;Id&gt;0&lt;/Id&gt;&lt;Key&gt;http://so.ard.iyyin.com/s/song_with_out?q=Emergency_20170115_215820%20%3Cunknown%3E&amp;amp;size=50&amp;amp;page=1&lt;/Key&gt;&lt;Metadata&gt;&amp;lt;DIDL-Lite xmlns:dc=&amp;quot;http://purl.org/dc/elements/1.1/&amp;quot; xmlns:upnp=&amp;quot;urn:schemas-upnp-org:metadata-1-0/upnp/&amp;quot; xmlns:song=&amp;quot;www.wiimu.com/song/&amp;quot; xmlns=&amp;quot;urn:schemas-upnp-org:metadata-1-0/DIDL-Lite/&amp;quot;&amp;gt; &amp;lt;upnp:class&amp;gt;object.item.audioItem.musicTrack&amp;lt;/upnp:class&amp;gt; &amp;lt;item&amp;gt; &amp;lt;song:bitrate&amp;gt;0&amp;lt;/song:bitrate&amp;gt; &amp;lt;song:id&amp;gt;0&amp;lt;/song:id&amp;gt;&amp;lt;song:singerid&amp;gt;0&amp;lt;/song:singerid&amp;gt;&amp;lt;song:albumid&amp;gt;0&amp;lt;/song:albumid&amp;gt;&amp;lt;res protocolInfo=&amp;quot;http-get:*:audio/mpeg:DLNA.ORG_PN=MP3;DLNA.ORG_OP=01;&amp;quot; duration=&amp;quot;5480&amp;quot;&amp;gt;<replace_with_mp3_file>&amp;lt;/res&amp;gt;&amp;lt;dc:title&amp;gt;Emergency_20170115_215820&amp;lt;/dc:title&amp;gt; &amp;lt;upnp:artist&amp;gt;&amp;amp;lt;unknown&amp;amp;gt;&amp;lt;/upnp:artist&amp;gt; &amp;lt;upnp:album&amp;gt;&amp;amp;lt;unknown&amp;amp;gt;&amp;lt;/upnp:album&amp;gt; &amp;lt;upnp:albumArtURI&amp;gt;&amp;lt;/upnp:albumArtURI&amp;gt; &amp;lt;/item&amp;gt; &amp;lt;/DIDL-Lite&amp;gt; &lt;/Metadata&gt;&lt;/Track1&gt;&lt;/Tracks&gt;&lt;/PlayList&gt;</QueueContext></u:AppendTracksInQueue>"""
BROWSE_QUEUE = """<u:BrowseQueue xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueName>CurrentQueue</QueueName></u:BrowseQueue></s:Body></s:Envelope>"""
SET_PLAY_MODE = """<u:SetPlayMode xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><NewPlayMode>NORMAL</NewPlayMode></u:SetPlayMode>"""
GET_PLAY_TYPE = """<u:GetPlayType xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetPlayType>"""
PLAY_QUEUE = """<u:PlayQueueWithIndex xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><QueueName>davanserver_tts_service</QueueName><Index>1</Index></u:PlayQueueWithIndex>"""
PLAY = """<u:Play xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID><Speed>1</Speed></u:Play>"""
PAUSE = """<u:Pause xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Pause>"""
STOP = """<u:Stop xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:Stop>"""
SET_VOLUME = """<u:SetVolume xmlns:u="urn:schemas-upnp-org:service:RenderingControl:1"><InstanceID>0</InstanceID><Channel>Single</Channel><DesiredVolume>30</DesiredVolume></u:SetVolume>"""
GET_INFO = """<u:GetInfoEx xmlns:u="urn:schemas-upnp-org:service:AVTransport:1"><InstanceID>0</InstanceID></u:GetInfoEx>"""

headers = {'content-type': 'text/xml;charset="utf-8"'}

URL_PLAY_QUEUE = "/upnp/control/PlayQueue1"
URL_RENDER_TRANSPORT = "/upnp/control/rendertransport1"
URL_RENDER_CONTROL = "/upnp/control/rendercontrol1"

def set_queue_loop_mode(host_address):
    logger.debug("execute command [set queue loop mode]")
    url = host_address + URL_PLAY_QUEUE
    headers = {'content-type': 'text/xml;charset="utf-8"','Soapaction':'"urn:schemas-wiimu-com:service:PlayQueue:1#SetQueueLoopMode"'}
    body = """<?xml version="1.0" encoding="utf-8" standalone="yes"?><s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:SetQueueLoopMode xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"><LoopMode>2</LoopMode></u:SetQueueLoopMode></s:Body></s:Envelope>"""
    send_command(url, body, headers)        

def get_queue_loop_mode(host_address):
    logger.debug("execute command [get queue loop mode]")
    url = host_address + URL_PLAY_QUEUE
    headers = {'content-type': 'text/xml;charset="utf-8"','Soapaction':'"urn:schemas-wiimu-com:service:PlayQueue:1#GetQueueLoopMode"'}
    body = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
    <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"><s:Body><u:GetQueueLoopMode xmlns:u="urn:schemas-wiimu-com:service:PlayQueue:1"></u:GetQueueLoopMode></s:Body></s:Envelope>"""
    send_command(url, body, headers)

def create_queue(host_address):
    logger.debug("execute command [create queue]")
    url = host_address + URL_PLAY_QUEUE
    headers['Soapaction'] = '"urn:schemas-wiimu-com:service:PlayQueue:1#CreateQueue"'
    body = XML_START_TAG + CREATE_QUEUE_TAG + XML_END_TAG 
    send_command(url, body, headers)

def replace_queue(host_address, msg):
    logger.debug("execute command [replace queue]")
    url = host_address + URL_PLAY_QUEUE
    headers['Soapaction'] = '"urn:schemas-wiimu-com:service:PlayQueue:1#ReplaceQueue"'
    queue_cmd = replace_queue_tag.replace('<replace_with_mp3_file>', msg)

    body = XML_START_TAG + queue_cmd + XML_END_TAG 
    send_command(url, body, headers)

def append_tracks_in_queue(host_address, msg):
    logger.debug("execute command [append tracks in queue]")
    url = host_address + URL_PLAY_QUEUE
    headers['Soapaction'] = '"urn:schemas-wiimu-com:service:PlayQueue:1#AppendTracksInQueue"'
    append = APPEND_TRACK_IN_QUEUE.replace('<replace_with_mp3_file>', msg)
    body = XML_START_TAG + append + XML_END_TAG

    send_command(url, body, headers)

def append_external_tracks_in_queue(host_address, msg):
    logger.debug("execute command [append tracks in queue]")
    url = host_address + URL_PLAY_QUEUE
    headers['Soapaction'] = '"urn:schemas-wiimu-com:service:PlayQueue:1#AppendTracksInQueue"'
    append = APPEND_EXT_TRACK_IN_QUEUE.replace('<replace_with_mp3_file>', msg)
    body = XML_START_TAG + append + XML_END_TAG

    send_command(url, body, headers)

def browse_queue(host_address):
    logger.debug("execute command [browse queue]")
    url = host_address + URL_PLAY_QUEUE
    headers['Soapaction'] = '"urn:schemas-wiimu-com:service:PlayQueue:1#BrowseQueue"'
    body = XML_START_TAG + BROWSE_QUEUE + XML_END_TAG
    send_command(url, body, headers)

def send_play_with_index(host_address):
    logger.debug("execute command [send play with index]")
    url = host_address + URL_PLAY_QUEUE
    headers['Soapaction'] = '"urn:schemas-wiimu-com:service:PlayQueue:1#PlayQueueWithIndex"'
    body = XML_START_TAG + PLAY_QUEUE + XML_END_TAG
    send_command(url, body, headers)

def set_play_mode(host_address):
    logger.debug("execute command [set play mode]")
    url = host_address + URL_RENDER_TRANSPORT
    headers['Soapaction'] = '"urn:schemas-upnp-org:service:AVTransport:1#SetPlayMode"'
    body = XML_START_TAG + SET_PLAY_MODE + XML_END_TAG
    send_command(url, body, headers)

def get_play_type(host_address):
    logger.debug("execute command [get play type]")
    url = host_address + URL_RENDER_TRANSPORT
    headers['Soapaction'] = '"urn:schemas-upnp-org:service:AVTransport:1#GetPlayType"'
    body = XML_START_TAG + GET_PLAY_TYPE + XML_END_TAG
    send_command(url, body, headers)
    
def pause(host_address):
    logger.debug("execute command [send pause]")
    url = host_address + URL_RENDER_TRANSPORT
    headers['Soapaction'] ='"urn:schemas-upnp-org:service:AVTransport:1#Pause"'
    body = XML_START_TAG + PAUSE + XML_END_TAG
    send_command(url, body, headers)

def stop(host_address):
    logger.debug("execute command [send stop]")
    url = host_address + URL_RENDER_TRANSPORT
    headers['Soapaction'] = '"urn:schemas-upnp-org:service:AVTransport:1#Stop"'
    body = XML_START_TAG + STOP + XML_END_TAG
    send_command(url, body, headers)

def send_play(host_address):
    logger.debug("execute command [send play]")
    url = host_address + URL_RENDER_TRANSPORT
    headers['Soapaction'] = '"urn:schemas-upnp-org:service:AVTransport:1#Play"'
    body = XML_START_TAG + PLAY + XML_END_TAG 
    send_command(url, body, headers)

def set_volume(host_address):
    logger.debug("execute command [set volume]")
    url = host_address + URL_RENDER_CONTROL
    headers['Soapaction'] ='"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"'
    body = XML_START_TAG + SET_VOLUME + XML_END_TAG
    send_command(url, body, headers)
        
def get_info(host_address):
    logger.debug("execute command [get info]")
    url = host_address + URL_RENDER_TRANSPORT
    headers['Soapaction'] = '"urn:schemas-upnp-org:service:AVTransport:1#GetInfoEx"'
    body = XML_START_TAG + GET_INFO + XML_END_TAG
    return send_command(url, body, headers)

def send_command(url, body, headers):
    r = requests.post(url,data=body,headers=headers)
    logger.debug("Received response [" + str(r.status_code) +"]")
    return r