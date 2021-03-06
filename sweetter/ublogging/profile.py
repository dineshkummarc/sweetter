from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from ublogging import api
from ublogging.models import Profile
import flash
import ublogging


class OPT:
    def __init__(self, id, label, type, value):
        self.id = id
        self.label = label
        self.type = type
        self.value = value


@login_required
def profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'GET':
        opts = {}
        for p in ublogging.plugins:
            options = [getattr(p, i) for i in dir(p) if isinstance(getattr(p, i), api.PluginOpt)]
            options = [OPT(i.id, i.id.replace('_', ' '), i.get_html_type(), i.get_html_value(request)) for i in options]
            try:
                opts[p.__plugin_name__] = options
            except:
                pass

        apikey = profile.apikey

        return render_to_response('profile.html',
                {'options': opts,
                 'apikey': apikey,
                },
                context_instance=RequestContext(request))
    else:
        email = request.POST["email"]
        url = request.POST["url"]
        location = request.POST["location"]
        pw = request.POST["pw"]
        pw2 = request.POST["pw2"]

        if pw and pw != pw2:
            flash.set_flash(request, "Password confirmation fails. Changes not saved", "error")
            return HttpResponseRedirect(reverse('ublogging.views.profile'))
        elif pw:
            request.user.set_password(pw)
            request.user.save()

        profile.email = email
        profile.url = url
        profile.location = location
        profile.save()

        for p in ublogging.plugins:
            options = [getattr(p, i) for i in dir(p) if isinstance(getattr(p, i), api.PluginOpt)]
            if options:
                for opt in options:
                    try:
                        v = request.POST[opt.id]
                        opt.set(v, request.user.username)
                    except:
                        # checkbox to false
                        opt.set(False, request.user.username)

        flash.set_flash(request, "Preferences saved")
        return HttpResponseRedirect(reverse('ublogging.views.profile'))


@login_required
def renewapikey(request):
    profile = Profile.objects.get(user=request.user)
    profile.regen_apikey()
    profile.save()

    flash.set_flash(request, "ApiKey changed.")
    return HttpResponseRedirect(reverse('ublogging.views.profile'))
