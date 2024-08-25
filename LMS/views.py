from django.shortcuts import render,redirect,get_object_or_404
from app.models import Categories,Course,Level,Video,UserCourse,Payment,Blog
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.db.models import Sum
from django.contrib import messages
import razorpay
from django.views.decorators.csrf import csrf_exempt
from time import time 
from . settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))



def BASE(request): 
	return render(request, 'base.html')



def HOME(request):
    # Fetch categories
    category = Categories.objects.all().order_by('id')[:5]
    
    # Fetch published courses
    course = Course.objects.filter(status='PUBLISH').order_by('id')
    
    # Fetch latest blog posts (you can modify this query to suit your needs)
    blogs = Blog.objects.all().order_by('-created_at')[:5]

    # Pass data to the context
    context = {
        'category': category,
        'course': course,
        'blogs': blogs,
    }
    
    return render(request, 'Main/home.html', context)



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
	action = request.GET.get('action')
	order = None

	if course.price == 0:
		course = UserCourse(
			user =request.user,
			course = course,
			)
		course.save()
		messages.success(request, "Course are Successfully Enrolled")
		return redirect('mycourse')

	elif action == 'create_payment':
		if request.method == 'POST':

			first_name = request.POST.get('billing_first_name')
			last_name = request.POST.get('billing_last_name')
			email = request.POST.get('billing_email')
			phone = request.POST.get('billing_phone')
			address_1 = request.POST.get('billing_address_1')
			address_2 = request.POST.get('billing_address_2')
			city = request.POST.get('billing_city')
			state = request.POST.get('billing_state')
			pincode = request.POST.get('billing_pincode')
			order_comments = request.POST.get('order_comments')


			amount_cal = course.price - (course.price * course.discount) / 100

			amount = int(amount_cal) * 100
			currency = 'INR'
			receipt = f"internIQ{int(time())}"
			notes = {
			'email': email,
			'name' : f"{first_name} {last_name}",
			'phone': phone,
			'address': f'{address_1} {address_2}',
			'city': city,
			'state': state,
			'pincode': pincode,
			'order_comments': order_comments,
			}

			order = client.order.create(
			{'amount':amount, 
			'currency':currency, 
			'receipt':receipt, 
			'notes':notes})

			payment = Payment(
				course = course,
				user = request.user,
				order_id = order['id'],)

			payment.save()

	context = {
	'course': course,
	'order': order,
	}

	return render(request, "checkout/checkout.html",context)

@csrf_exempt
def VERIFY_PAYMENT(request):
	if request.method == 'POST':
		data = request.POST
		try:
			client.utility.verify_payment_signature(data)
			razorpay_order_id = data['razorpay_order_id']
			razorpay_payment_id = data['razorpay_payment_id']
			

			payment = Payment.objects.get(order_id = razorpay_order_id)
			payment.payment_id = razorpay_payment_id
			payment.status = True
			payment.save()

			usercourse = UserCourse(
				user = payment.user,
				course = payment.course,
				)
			course.save()
			payment.user_course = usercourse
			payment.save()

			context = {
			'payment': payment,
			'data': data,
			}
			return render(request, "verify_payment/success.html", context)

		except:
			return render(request, "verify_payment/fail.html")

	return redirect('home')


def MY_COURSE(request):
	if request.user.is_authenticated:	
		course = UserCourse.objects.filter(user = request.user)

		context = {
		'course': course
		}
		return render(request, "course/my_course.html",context)
	else:
		return redirect('login')




def WATCH_COURSE(request, slug):
    # Retrieve the course based on the slug
    course = get_object_or_404(Course, slug=slug)
    
    # Get the lecture number from the request
    lecture_number = request.GET.get('lecture')
    if lecture_number:
        try:
            # Convert lecture_number to integer
            lecture_number = int(lecture_number)
            
            # Retrieve the video based on course and serial number
            video = Video.objects.filter(course=course, serial_number=lecture_number).first()
            
            if not video:
                # If no video is found, redirect or handle accordingly
                return redirect('404')  # Adjust according to your error handling
        except ValueError:
            # Handle invalid lecture_number format
            return redirect('404')
    else:
        # Default to the first video if no lecture_number is provided
        video = Video.objects.filter(course=course).order_by('serial_number').first()
    
    if video:
        # Get the next and previous video IDs
        next_video = Video.objects.filter(course=course, serial_number__gt=video.serial_number).order_by('serial_number').first()
        prev_video = Video.objects.filter(course=course, serial_number__lt=video.serial_number).order_by('-serial_number').first()

        next_id = next_video.serial_number if next_video else None
        prev_id = prev_video.serial_number if prev_video else None
    else:
        next_id = None
        prev_id = None

    context = {
        'course': course,
        'video': video,
        'next_id': next_id,
        'prev_id': prev_id,
    }

    return render(request, "course/watch-course.html", context)


def blog_detail(request, slug):
    blogs = get_object_or_404(Blog, slug=slug)
    return render(request, 'Pages/page.html', {'blogs': blogs})

def PAGES_ALL(request):
    blogs = Blog.objects.all() 
    return render(request, 'Pages/all_pages.html', {'blogs': blogs})