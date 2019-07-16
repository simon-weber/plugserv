import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework import serializers


class User(AbstractUser):
    serve_id = models.UUIDField(default=uuid.uuid4, editable=False)
    ga_tracking_id = models.TextField(
        blank=True,
        help_text=('If set, impressions and clicks will be sent as events to this property.'
                   ' Requires setup in GA; see the docs for instructions.'),
        verbose_name='Google Analytics tracking id',
    )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        read_only_fields = ('username', 'serve_id')
        fields = read_only_fields + ('ga_tracking_id',)


class Plug(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    domain = models.TextField(
        help_text=('The domain of the site being linked to, eg <code>www.example.com</code>.'
                   ' Plugs will not be served to origins with the <i>exact</i> same domain'
                   ' (to prevent plugging a site a user is already on).'
                   ' Subdomains do not get special treatment; a www.example.com plug may be served to example.com or app.example.com.')
    )
    html_content = models.TextField(
        help_text=('The HTML to replace your plug elements with, eg'
                   ' <code>Check out &lt;a href="http://www.example.com"&gt;my blog&lt;/a&gt;!</code>.')
    )

    def __str__(self):
        return "%s: %r" % (
            self.id,
            self.domain,
        )


class PlugSerializer(serializers.HyperlinkedModelSerializer):
    # keep in mind this information is all public
    class Meta:
        model = Plug
        fields = ('url', 'domain', 'html_content',)
