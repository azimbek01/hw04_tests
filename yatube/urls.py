from django.contrib import admin
from django.urls import include, path
from django.contrib.flatpages import views


urlpatterns = [
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls'))
]

urlpatterns += [
    path('about-author/', views.flatpage, {'url': '/about-author/'},
         name='/about-author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'},
         name='/about-spec')
]
