from django.shortcuts import render,redirect
from app.models import Categories,Course,Level,Video,UserCourse
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages

def BASE(request): 
	return render(request, 'base.html')


def HOME(request): 
	category = Categories.objects.all().order_by('id')[0:5]
	course = Course.objects.filter(status='PUBLISH').order_by('id')
	context = {
	'category': category,
	'course': course
	}
	return render(request, 'Main/home.html',context)


def SINGLE_COURSE(request): 
	category = Categories.get_all_category(Categories)
	level = Level.objects.all()
	course = Course.objects.all()
	context = {
	'category': category,
	'level':level,
	'course':course,
	}

	return render(request, 'Main/single_course.html',context)

def CONTACT(request): 
	category = Categories.get_all_category(Categories)


	context = {
	'category': category
	}
	return render(request, 'Main/contact_us.html',context)

def ABOUT(request): 

	category = Categories.get_all_category(Categories)
	

	context = {
	'category': category
	}
	return render(request, 'Main/about_us.html',context)



def filter_data(request):
    categories = request.GET.getlist('category[]')
    level = request.GET.getlist('level[]')
    price = request.GET.getlist('price[]')
    print(price)


    if price == ['pricefree']:
       course = Course.objects.filter(price=0)
    elif price == ['pricepaid']:
       course = Course.objects.filter(price__gte=1)
    elif price == ['priceall']:
       course = Course.objects.all()
    elif categories:
       course = Course.objects.filter(category__id__in=categories).order_by('-id')
    elif level:
       course = Course.objects.filter(level__id__in = level).order_by('-id')
    else:
       course = Course.objects.all().order_by('-id')


    t = render_to_string('ajax/course.html', {'course': course})

    return JsonResponse({'data': t})



def SEARCH_COURSE(request):


	
   query = request.GET['query']
   course = Course.objects.filter(title__icontains = query)
   context = {
        'course':course,
        	
   }
   return render(request,'search/search.html',context)


def COURSE_DETAILS(request,slug):

	if request.user.is_authenticated:


		category = Categories.get_all_category(Categories) 
		time_duration = Video.objects.filter(course__slug=slug).aggregate(sum=Sum('time_duration'))

		course = Course.objects.filter(slug=slug)
		course_id = Course.objects.get(slug=slug)

		try:
			check_enroll = UserCourse.objects.get(user = request.user, course= course_id)
		except UserCourse.DoesNotExist:
			check_enroll = None

		if course.exists():

			course = course.first()
		else:
			return redirect('404')

		context = {
		'course' : course,
		'category': category,
		'time_duration':time_duration,
		'check_enroll': check_enroll
		}
		return render(request, "course/course_details.html", context)

	else:
		return redirect("login")


def PAGE_NOT_FOUND(request):
	return render(request, "error/404.html")


def CHECKOUT(request,slug):

	course = Course.objects.get(slug=slug)


	if course.price == 0:
		course = UserCourse(
			user =request.user,
			course = course,
			)
		course.save()
		messages.success(request, "Course are Successfully Enrolled")
		return redirect('mycourse')

	return render(request, "checkout/checkout.html")



def MY_COURSE(request):
	if request.user.is_authenticated:	
		course = UserCourse.objects.filter(user = request.user)

		context = {
		'course': course
		}
		return render(request, "course/my_course.html",context)
	else:
		return redirect('login')




def WATCH_COURSE(request,slug):

	course = Course.objects.filter(slug=slug)
	next_id = 2
	prev_id = 1
	

	leccture = request.GET.get('lecture')
	if leccture:
		video = Video.objects.get(id=leccture)
		next_id = int(leccture) + 1
		prev_id = int(leccture) -1
	else:
		leccture = 1

		video = Video.objects.get(id=leccture)
	if course.exists():

		course = course.first()
	else:
		return redirect('404') 



	context = {
	'courseto':course,
	'video':video,
	'next_id': next_id,
	'prev_id':prev_id
	}

	return render(request, "course/watch-course.html",context)