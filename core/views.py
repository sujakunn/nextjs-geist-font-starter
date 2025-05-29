from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Module, Unit, Assessment, Question, UserProgress
from django.utils import timezone

def home(request):
    """Home page view showing featured courses"""
    courses = Course.objects.all()[:4]  # Get first 4 courses
    return render(request, 'core/home.html', {
        'courses': courses
    })

@login_required
def dashboard(request):
    """User dashboard showing available modules"""
    modules = Module.objects.all()
    
    # Add default descriptions if not present
    for module in modules:
        if not module.description:
            module.description = "Klik untuk mempelajari materi ini"

    return render(request, 'core/dashboard.html', {
        'modules': modules
    })

def course_list(request):
    """List all available courses"""
    courses = Course.objects.all()
    return render(request, 'core/course_list.html', {
        'courses': courses
    })

def course_detail(request, pk):
    """Show detailed information about a course and its modules"""
    course = get_object_or_404(Course, pk=pk)
    modules = course.modules.all().prefetch_related('units')
    
    if request.user.is_authenticated:
        # Get user progress for this course
        user_progress = UserProgress.objects.filter(
            user=request.user,
            unit__module__course=course
        ).select_related('unit')
        
        # Create a dict of completed units
        completed_units = {progress.unit_id: progress for progress in user_progress}
    else:
        completed_units = {}

    return render(request, 'core/course_detail.html', {
        'course': course,
        'modules': modules,
        'completed_units': completed_units
    })

@login_required
def module_detail(request, module_pk):
    """Show detailed information about a module and its units"""
    module = get_object_or_404(Module, pk=module_pk)
    units = module.units.all().order_by('order')
    
    if request.method == 'POST':
        unit_id = request.POST.get('unit')
        if unit_id:
            # Get or create assessment for this unit
            unit = get_object_or_404(Unit, pk=unit_id)
            assessment, created = Assessment.objects.get_or_create(
                unit=unit,
                defaults={
                    'title': f'Assessment for {unit.title}',
                    'description': 'Complete this assessment to progress.',
                    'assessment_type': 'quiz'
                }
            )
            return redirect('assessment', pk=assessment.id)
    
    # Get user progress for all units in this module
    user_progress = UserProgress.objects.filter(
        user=request.user,
        unit__module=module
    ).select_related('unit')
    
    # Create a dict of completed units
    completed_units = {progress.unit_id: progress for progress in user_progress}

    return render(request, 'core/module_detail.html', {
        'module': module,
        'units': units,
        'completed_units': completed_units
    })

@login_required
def assessment_view(request, pk):
    """Show assessment questions"""
    assessment = get_object_or_404(Assessment, pk=pk)
    questions = assessment.questions.all().prefetch_related('answers')
    
    return render(request, 'core/assessment.html', {
        'assessment': assessment,
        'questions': questions
    })

@login_required
def submit_assessment(request, pk):
    """Handle assessment submission"""
    if request.method != 'POST':
        return redirect('assessment', pk=pk)
        
    assessment = get_object_or_404(Assessment, pk=pk)
    questions = assessment.questions.all().prefetch_related('answers')
    
    # Calculate score
    total_questions = questions.count()
    correct_answers = 0
    
    for question in questions:
        submitted_answer_id = request.POST.get(f'question_{question.id}')
        if submitted_answer_id:
            correct_answer = question.answers.filter(is_correct=True).first()
            if correct_answer and str(correct_answer.id) == submitted_answer_id:
                correct_answers += 1
    
    score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    # Update user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        unit=assessment.unit
    )
    progress.score = score
    progress.completed = True
    progress.completed_at = timezone.now()
    progress.save()
    
    messages.success(request, f'Assessment completed! Your score: {score:.1f}%')
    return redirect('module_detail', module_pk=assessment.unit.module.id)

@login_required
def initial_assessment(request):
    if request.method == 'POST':
        answers = {
            'q1': request.POST.get('q1'),
            'q2': request.POST.get('q2'),
            'q3': request.POST.get('q3'),
            'q4': request.POST.get('q4'),
            'q5': request.POST.get('q5'),
        }
        correct_answers = {'q1': '8', 'q2': '6', 'q3': '8', 'q4': '4', 'q5': '13'}
        score = 0
        for key, correct in correct_answers.items():
            if answers.get(key) == correct:
                score += 20

        request.session['assessment_score'] = score
        return redirect('assessment_result')

    return render(request, 'core/initial_assessment.html')

@login_required
def assessment_result(request):
    score = request.session.get('assessment_score')
    if score is None:
        messages.error(request, "Tidak ada hasil assessment yang ditemukan.")
        return redirect('initial_assessment')

    if score >= 80:
        feedback = "Anda memiliki pemahaman yang sangat baik!"
    elif score >= 50:
        feedback = "Anda memiliki pemahaman yang cukup, tapi perlu latihan lebih."
    else:
        feedback = "Anda perlu memperdalam materi dasar matematika."

    context = {
        'score': score,
        'feedback': feedback,
    }
    return render(request, 'core/assessment_result.html', context)

@login_required
def module_recommendation(request):
    score = request.session.get('assessment_score')
    if score is None:
        messages.error(request, "Tidak ada hasil assessment yang ditemukan.")
        return redirect('initial_assessment')

    if score >= 80:
        modules = Module.objects.filter(title__icontains='Lanjutan')
    elif score >= 50:
        modules = Module.objects.filter(title__icontains='Menengah')
    else:
        modules = Module.objects.filter(title__icontains='Dasar')

    if not modules.exists():
        modules = Module.objects.all()

    for module in modules:
        if not hasattr(module, 'thumbnail_url'):
            module.thumbnail_url = 'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg'

    context = {
        'modules': modules,
    }
    return render(request, 'core/module_recommendation.html', context)
