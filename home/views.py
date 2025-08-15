from django.shortcuts import render

# main 페이지
def main(request):
    return render(request,'home/main.html') 