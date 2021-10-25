from flask import Flask, request
import types
import pyodbc
import base64
app = Flask(__name__)


@app.route("/")
def home():
    return "<h1>Dynamicfunctionreation</h1>"


def executeStatement(connections, ops, templates, target):
    def prepareStatement(ops, templates):
        msOplist = []
        orclOplist = []
        for op in ops:
            for opNumber in ops[op]['opNumber']:
                str_statement = templates[opNumber]['statement']
                str_statement = str_statement.replace('<%' + templates[opNumber]['id_number'] + '%>',
                                                      ops[op][templates[opNumber]['id_number']])
                str_statement = str_statement.replace('<%' + templates[opNumber]['id_type'] + '%>',
                                                      ops[op][templates[opNumber]['id_type']])
                opsInfo = {"statement": str_statement, "connid": templates[opNumber]['connid'], "opNumber": opNumber, "statementType": templates[opNumber]['statementType']}
                if templates[opNumber]['connectionType'] == "mssql":
                    msOplist.append(opsInfo)
                else:
                    orclOplist.append(opsInfo)

        return msOplist, orclOplist

    def passwordEncoding(password):
        base64_message = password
        base64_bytes = base64_message.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')
        return message

    msOplist, orclOplist = prepareStatement(ops, templates)

    def prepareConnection(connections, ops, templates):
        connectionList = {}

        for mssql in connections[target]['MSSQL']:
            driver = connections[target]['MSSQL'][mssql]['DRIVER']
            server = connections[target]['MSSQL'][mssql]['SERVER']
            database = connections[target]['MSSQL'][mssql]['database']
            username = connections[target]['MSSQL'][mssql]['username']
            #password = connections[target]['MSSQL'][mssql]['password']
            password = passwordEncoding(connections[target]['MSSQL'][mssql]['password'])
            cnxn = "DRIVER=<%driver%>;SERVER=<%server%>;DATABASE=<%database%>';UID=<%username%>';PWD=<%password%>)"

            cnxn = cnxn.replace('<%driver%>', driver)
            cnxn = cnxn.replace('<%server%>', server)
            cnxn = cnxn.replace('<%database%>', database)
            cnxn = cnxn.replace('<%username%>', username)
            cnxn = cnxn.replace('<%password%>', password)
            connectionList[mssql] = cnxn

        for orcl in connections[target]['ORCL']:
            hostname = connections[target]['ORCL'][orcl]['hostname']
            port = connections[target]['ORCL'][orcl]['port']
            service = connections[target]['ORCL'][orcl]['service/sid']
            username = connections[target]['ORCL'][orcl]['username']
            password = connections[target]['ORCL'][orcl]['username']
            cnxn = "<%username%>/<%password%>@<%hostname%>:<%port%>/<%service%>"

            cnxn = cnxn.replace('<%hostname%>', hostname)
            cnxn = cnxn.replace('<%port%>', port)
            cnxn = cnxn.replace('<%service%>', service)
            cnxn = cnxn.replace('<%username%>', username)
            cnxn = cnxn.replace('<%password%>', password)
            connectionList[orcl] = cnxn

        return connectionList

    connectionList = prepareConnection(connections, ops, templates)

    auditList = {}

    def msSqlExecution(msOplist, connectionList):
        # print("mssql connecetion--------")
        for op in msOplist:
            op_cnnx_str = connectionList[op['connid']]
            # print(op['opNumber'])
            # print(op_cnnx_str)
            # cnxn = pyodbc.connect(op_cnnx_str)
            # cursor = cnxn.cursor()
            if op['statementType']=="dml":

                op_statement = op['statement']
                # print(op_statement)
                auditList[op['opNumber']] = "dml executed succesfully"
                # cursor.execute(op_statement)
                # cnxn.commit()
            else:
                op_statement = op['statement']
                # print(op_statement)
                auditList[op['opNumber']] = "query executed succesfully"
                # cursor.execute(op_statement)

    def orclExecution(orclOplist, connectionList):
        # print("orcl connecetion--------")
        for op in orclOplist:
            op_cnnx_str = connectionList[op['connid']]
            # print(op['opNumber'])
            # print(op_cnnx_str)
            # cnxn = pyodbc.connect(op_cnnx_str)
            # cursor = cnxn.cursor()
            if op['statementType']=="dml":

                op_statement = op['statement']
                # print(op_statement)
                auditList[op['opNumber']] = "dml executed succesfully"
                # cursor.execute(op_statement)
                # cnxn.commit()
            else:
                op_statement = op['statement']
                # print(op_statement)
                auditList[op['opNumber']] = "query executed succesfully"
                # cursor.execute(op_statement)

    msSqlExecution(msOplist, connectionList)
    orclExecution(orclOplist, connectionList)

    return auditList


@app.route("/query")
def query():
    content = request.json
    connections = content['CONNECTIONS']

    ops = content['OPS']
    templates = content['TEMPLATES']
    target = content['TARGET']

    #### for dynamic function call ###
    # func = content['EXECUTESTATEMENT']
    # code = compile(func, '<string>', 'exec')
    # f_code = code.co_consts[0]
    # executeStatement = types.FunctionType(f_code, {}, name="executeStatement")
    # oplist = executeStatement(connections,ops,templates)
    # print(oplist)
    print(executeStatement(connections, ops, templates, target))
    return content['OPS']


app.run(host="0.0.0.0", port=9080, debug=False)
