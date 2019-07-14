from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^login/$',views.login,name="login"),
    url(r'^$',views.show,name='show'),
    url(r'^register/$',views.register,name='register'),
    url(r'^logout/$',views.logout,name='logout'),
    url(r'^verify/$',views.verify,name='verify'),
    url(r"^signup/(?P<user>\w+)/$", views.signUp , name="signup"),
]