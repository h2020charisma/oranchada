# + tags=["parameters"]
import uuid
import json
import h5pyd
from datetime import date
upstream = []
product = None
hs_endpoint = None
hsds_investigation = None
hs_username = None
hs_password = None
keycloak_server_url = None
keycloak_client_id = None
keycloak_realm_name = None

# -

from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from keycloak import KeycloakOpenID
from pynanomapper.clients.authservice import TokenService
from pynanomapper.clients.service_charisma import H5Service


class Container(containers.DeclarativeContainer):
    kcclient = providers.Singleton(
        KeycloakOpenID,
        server_url=keycloak_server_url,
        client_id=keycloak_client_id,
        realm_name=keycloak_realm_name,
        client_secret_key="secret"
    )
    tokenservice = providers.Factory(
        TokenService,
        kcclient = kcclient
    )
    h5service = providers.Factory(
        H5Service,
        tokenservice = tokenservice
    )


@inject
def main(ts = Provide[Container.h5service]):
    ts.login(hs_admin_username,hs_admin_password)
    try:
        domain = "/{}/".format(hsds_investigation)
        _folder = ts.create_domain(domain)
        print(_folder)

    except Exception as err:
        print(err)
    finally:
        ts.logout()



print(__name__)
container = Container()
container.init_resources()
container.wire(modules=[__name__])
main()
