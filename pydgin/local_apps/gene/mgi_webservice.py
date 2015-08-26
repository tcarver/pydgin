
from xml.dom.minidom import DOMImplementation, parseString
import requests


# define namespaces used
ec = "http://schemas.xmlsoap.org/soap/encoding/"
soapEnv = "http://schemas.xmlsoap.org/soap/envelope/"
req = "http://ws.mgi.jax.org/xsd/request"
bt = "http://ws.mgi.jax.org/xsd/batchType"

# create DOM document
domdoc = DOMImplementation().createDocument(None, None, None)

# create SOAP envelope and namespace
seObj = domdoc.createElementNS(soapEnv, "soapenv:Envelope")
seObj.setAttributeNS(soapEnv, "xmlns:soapenv", soapEnv)

# add SOAP envelope to the root
domdoc.appendChild(seObj)

# create SOAP header and add it to the SOAP envelope
header = domdoc.createElement("soapenv:Header")
seObj.appendChild(header)

# create SOAP body and add it to the SOAP envelope
body = domdoc.createElement("soapenv:Body")

# create submitDocument element
submitDoc = domdoc.createElement("submitDocument")
submitDoc.setAttributeNS(soapEnv, "xmlns:req", req)
submitDoc.setAttributeNS(soapEnv, "xmlns:bt", bt)


# create the desired ws_request element and sub-elements 
# in the appropriate namespace

# ws_request is a batchMarkerRequest
ws_request = domdoc.createElementNS(req, "req:batchMarkerRequest")

# create IDSet and assign appropriate IDType attribute
idset = domdoc.createElementNS(req, "req:IDSet")
idset.setAttribute("IDType", "symbol")

# create id elements and add to IDSet element
id1 = domdoc.createElementNS(bt, "bt:id")
id1.appendChild(domdoc.createTextNode("pax6"))
id2 = domdoc.createElementNS(bt, "bt:id")
id2.appendChild(domdoc.createTextNode("trp53"))

# add id elements to IDSet element
idset.appendChild(id1)
idset.appendChild(id2)

# create resturnSet element and sub-elements
returnSet = domdoc.createElementNS(req, "req:returnSet")
att1 = domdoc.createElementNS(bt, "bt:attribute")
att1.appendChild(domdoc.createTextNode("nomenclature"))
returnSet.appendChild(att1)
att2 = domdoc.createElementNS(bt, "bt:attribute")
att2.appendChild(domdoc.createTextNode("location"))
returnSet.appendChild(att2)
att3 = domdoc.createElementNS(bt, "bt:attribute")
att3.appendChild(domdoc.createTextNode("entrezGene"))
returnSet.appendChild(att3)
att4 = domdoc.createElementNS(bt, "bt:attribute")
att4.appendChild(domdoc.createTextNode("ensembl"))
returnSet.appendChild(att4)
att5 = domdoc.createElementNS(bt, "bt:attribute")
att5.appendChild(domdoc.createTextNode("vega"))
returnSet.appendChild(att5)

# create returnAdditionalInfo element
additionalInfo = domdoc.createElementNS(req, "req:returnAdditionalInfo")
additionalInfo.appendChild(domdoc.createTextNode("mp"))

# add IDSet to batchMarkerRequest element
ws_request.appendChild(idset)

# add resturnSet to batchMarkerRequest element
ws_request.appendChild(returnSet)

# add returnAdditionalInfo to batchMarkerRequest element
ws_request.appendChild(additionalInfo)

# add batchMarkerRequest to submitDocument element
submitDoc.appendChild(ws_request)

# add submitDocument to SOAP body
body.appendChild(submitDoc)

# add SOAP body to SOAP envelope
seObj.appendChild(body)

soapStrOut = domdoc.toprettyxml()
print(soapStrOut)
headers = {
    "Content-type": 'text/xml; charset="UTF-8"',
    "SOAPAction": "submitDocument",
    "Content-length": "%d" % len(soapStrOut)
    }
resp = requests.post("http://services.informatics.jax.org/mgiws",
                     data=soapStrOut, headers=headers)

dom_resp = parseString(resp.content.decode("utf-8"))
print(dom_resp.toprettyxml())
