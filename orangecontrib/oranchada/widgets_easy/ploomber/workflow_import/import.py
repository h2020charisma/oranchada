# + tags=["parameters"]
upstream = []
product = None
metadata = None
ramandb_api = None
hsds_investigation = None
dry_run = None
keycloak_server_url = None
keycloak_client_id = None
keycloak_realm_name = None
hs_username = None
hs_password = None

# -


from dependency_injector import containers, providers
from dependency_injector.wiring import Provide, inject
from keycloak import KeycloakOpenID
from pynanomapper.clients.authservice import TokenService
from pynanomapper.clients.service_import import ImportService
import traceback




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

    importservice = providers.Factory(
        ImportService,
        tokenservice = tokenservice,
        ramandb_api = ramandb_api,
        hsds_investigation = hsds_investigation,
        dry_run = dry_run
    )


@inject
def main(importservice = Provide[Container.importservice], ):
    importservice.login(hs_username,hs_password)
    try:
        metadata_file = metadata     
        importservice.import2hsds(metadata_file,product["data"])
    except Exception as err:
        traceback.print_exc()
    finally:
        importservice.logout()


print(__name__)
container = Container()
container.init_resources()
container.wire(modules=[__name__])
main()
