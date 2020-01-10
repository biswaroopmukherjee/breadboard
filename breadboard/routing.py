from channels.routing import ProtocolTypeRouter, URLRouter
import api.routing

application = ProtocolTypeRouter({
    'http': URLRouter(api.routing.urlpatterns),
})