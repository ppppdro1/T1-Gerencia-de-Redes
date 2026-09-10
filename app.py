from flask import Flask, render_template
import asyncio

from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine,
    CommunityData,
    UdpTransportTarget,
    ContextData,
    ObjectType,
    ObjectIdentity,
    get_cmd
)

app = Flask(__name__)

SNMP_HOST = "127.0.0.1"
SNMP_PORT = 161
SNMP_COMMUNITY = "public"


async def consultar_snmp(oid):

    snmpEngine = SnmpEngine()

    try:
        transport = await UdpTransportTarget.create(
            (SNMP_HOST, SNMP_PORT)
        )

        error_indication, error_status, error_index, var_binds = await get_cmd(
            snmpEngine,
            CommunityData(SNMP_COMMUNITY, mpModel=1),
            transport,
            ContextData(),
            ObjectType(ObjectIdentity(oid))
        )

        if error_indication:
            return f"Erro: {error_indication}"

        if error_status:
            return f"Erro: {error_status.prettyPrint()}"

        for var_bind in var_binds:
            return str(var_bind[1])

    except Exception as e:
        return f"Erro: {e}"

    finally:
        snmpEngine.close_dispatcher()


def consultar(oid):
    valor = asyncio.run(consultar_snmp(oid))

    if oid == "1.3.6.1.2.1.1.3.0":
        try:
            ticks = int(valor)
            segundos = ticks / 100

            dias = int(segundos // 86400)
            horas = int((segundos % 86400) // 3600)
            minutos = int((segundos % 3600) // 60)
            segundos_restantes = int(segundos % 60)

            if dias > 0:
                return f"{dias} dias, {horas:02d}:{minutos:02d}:{segundos_restantes:02d}"

            return f"{horas:02d}:{minutos:02d}:{segundos_restantes:02d}"

        except ValueError:
            return valor

    return valor


@app.route("/")
def index():

    dados = {
        "Nome": consultar("1.3.6.1.2.1.1.5.0"),
        "Descrição": consultar("1.3.6.1.2.1.1.1.0"),
        "Tempo ligado": consultar("1.3.6.1.2.1.1.3.0"),
        "Localização": consultar("1.3.6.1.2.1.1.6.0"),
        "Contato": consultar("1.3.6.1.2.1.1.4.0")
    }

    return render_template("index.html", dados=dados)


if __name__ == "__main__":
    app.run(debug=True)