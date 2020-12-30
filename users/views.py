from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from register_and_login.models import Dog, Profile


@login_required
def profile(request):
    context = { 'dogs' : Dog.objects.all().filter(owner_id=request.user.profile.id) }

    return render(request, 'users/profile.html', context) 

GOOGLE_MAP_KEY = 'AIzaSyBBcPbX-93uzhQq9qQosN7TzVYGtr3cFpg'
import urllib.request
import json

def check_location(location_A,location_B,helping_radius):
    url = '''https://maps.googleapis.com/maps/api/distancematrix/json?units=metric&origins={}&destinations={}&key={}'''.format(location_A,location_B,GOOGLE_MAP_KEY)
    response = urllib.request.urlopen(url)
    result = json.loads(response.read())
    status = result['rows'][0]['elements'][0]['status']
    if status == 'OK':
        distance = [result['rows'][0]['elements'][0]['distance']['text'],{'m':result['rows'][0]['elements'][0]['distance']['value']}]
        # with open("data.txt",'w') as file: # Use file to refer to the file object
        #     file.write(str(distance[1]['m']))
        # expected_time = [result['rows'][0]['elements'][0]['duration']['text'],{'s':result['rows'][0]['elements'][0]['duration']['value']}]
        return True if float(distance[1]['m']) <= float(helping_radius*1000) else False 

def find_smallest_dog(list_of_dogs):
    size_values = {'S':1,'M':2,'B':3}
    smallest_dog = 'B'
    for dog in list_of_dogs:
        if size_values[dog.size] < size_values[smallest_dog]:
            smallest_dog = dog.size
    return smallest_dog

def check_dog_size(temp_user_dog, helper_max_size_dog):
    size_values = {'S':1,'M':2,'B':3}
    return True if size_values[temp_user_dog] <= size_values[helper_max_size_dog] else False


def check_time(helper, time_period_id):

    helper_time_period = TimePeriod.objects.all().filter( person_id = helper.user_id ).filter(time_type = 'F')
    needy_time_period = TimePeriod.objects.all().filter( id__in = time_period_id ).filter(time_type = 'F')

    data = []
    for helper_time in helper_time_period:
        for needy_time in needy_time_period:
            if (helper_time.day == needy_time.day) and (helper_time.start_hour == needy_time.start_hour ) and (helper_time.end_hour == needy_time.end_hour):
                # data.append({'helper':helper_time,'needy':needy_time})
                data.append(helper_time)
    return data



def chat(request):
    data = []
    temp_user = Profile.objects.all().filter(user = request.user)
    temp_user_dogs = Dog.objects.all().filter(owner_id = temp_user[0].id)
    temp_user_dogs_id = [ dog.id for dog in temp_user_dogs ] 

    helpers = Profile.objects.all().filter(account_type='H')
    list_of_helpers_distance = [ helpers[i] for i in range(helpers.count()) if check_location( temp_user[0].location, helpers[i].location, helpers[i].helping_radius) ]

    dogs = DogTime.objects.all().filter(dog_id__in = temp_user_dogs_id).filter(match = False) 
    
    smallest_dog_size = find_smallest_dog(Dog.objects.all().filter( id__in =  dogs ))

    time_period_id = [ dog.time_period_id for dog in dogs ]

    list_of_helpers_time = [ ]
    match_time_data = []
    for helper in list_of_helpers_distance:
        data = check_time( helper, time_period_id )
        if len(data) != 0:
            list_of_helpers_time.append(helper)
            match_time_data.append(data)

    list_of_helpers_dogs_size = [ helper for helper in list_of_helpers_time if check_dog_size(smallest_dog_size ,helper.max_dog_size )]
    

    return render(request, 'users/data.html',{'data':list_of_helpers_time,'match':match_time_data}) 

























from datetime import datetime, timedelta, date
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.utils.safestring import mark_safe
import calendar

from register_and_login.models import DogTime, TimePeriod
from .utils import Calendar

class CalendarView(generic.ListView):
    model = TimePeriod
    template_name = 'users/calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        view = self.request.GET.get('view', None)
        date = self.request.GET.get('date', None)
        user = self.request.user
        events = TimePeriod.objects.filter(person=user)
        if date:
            d = datetime.strptime(date, '%Y-%m-%d')
        else:
            d = datetime.now()
        cal = Calendar(d.year, d.month, d.day)
        if view=='day':
            html_cal = cal.formatbyday(events, withyear=True)
            context['prev_view'] = (d - timedelta(days=1)).strftime("%Y-%m-%d")
            context['next_view'] = (d + timedelta(days=1)).strftime("%Y-%m-%d")
        elif view=='week':
            html_cal = cal.formatbyweek(events, withyear=True)
            context['prev_view'] = (d - timedelta(days=7)).strftime("%Y-%m-%d")
            context['next_view'] = (d + timedelta(days=7)).strftime("%Y-%m-%d")
        else:
            html_cal = cal.formatmonth(events, withyear=True)
            context['prev_view'] = (d.replace(day=1) - timedelta(days=1)).strftime("%Y-%m-%d")
            context['next_view'] = (d.replace(day=calendar.monthrange(d.year, d.month)[1]) + timedelta(days=1)).strftime("%Y-%m-%d")

        context['calendar'] = mark_safe(html_cal)
        return context

from .utils import synchronize_with_google_calendar

def synchronize_calendar(request):
    synchronize_with_google_calendar(request)
    ####
    return render(request, 'users/calendar.html') 