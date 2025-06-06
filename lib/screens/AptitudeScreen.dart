import 'package:flutter/material.dart';
import 'package:your_app/services/api_service.dart';

class CategoryQuestionsScreen extends StatefulWidget {
  final String apiEndpoint;
  final String categoryName;

  const CategoryQuestionsScreen({Key? key, required this.apiEndpoint, required this.categoryName}) : super(key: key);

  @override
  _CategoryQuestionsScreenState createState() => _CategoryQuestionsScreenState();
}

class _CategoryQuestionsScreenState extends State<CategoryQuestionsScreen> {
  List<dynamic> _questions = [];
  bool _isLoading = false;
  int _currentQuestionIndex = 0;
  int? _selectedAnswerIndex;
  bool _answerChecked = false;
  int _score = 0;
  bool _isSubmitting = false;

  @override
  void initState() {
    super.initState();
    _fetchQuestions();
  }

  Future<void> _fetchQuestions() async {
    setState(() {
      _isLoading = true;
    });
    try {
      final questions = await ApiService.fetchQuestions(widget.apiEndpoint);
      setState(() {
        _questions = questions;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  Future<void> _submitScore() async {
    setState(() {
      _isSubmitting = true;
    });

    try {
      final response = await ApiService.submitAptitudeScore(_score, widget.categoryName);
      
      if (response != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Score submitted successfully! Average: ${response['avg_aptitude_score']}'),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      String errorMessage = 'Error submitting score';
      if (e.toString().contains('Authentication failed') || e.toString().contains('No authentication token')) {
        errorMessage = 'Please login again to submit your score';
        // Optionally navigate to login screen
        // Navigator.pushReplacementNamed(context, '/login');
      }
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(errorMessage),
          backgroundColor: Colors.red,
          action: SnackBarAction(
            label: 'Login',
            onPressed: () {
              // Navigate to login screen
              // Navigator.pushReplacementNamed(context, '/login');
            },
          ),
        ),
      );
    } finally {
      setState(() {
        _isSubmitting = false;
      });
    }
  }

  void _checkAnswer() {
    if (_selectedAnswerIndex != null) {
      setState(() {
        _answerChecked = true;
        if (_questions[_currentQuestionIndex]['options'][_selectedAnswerIndex]['correct']) {
          _score++;
        }
      });
    }
  }

  void _goToNextQuestion() async {
    if (_questions.isNotEmpty && _currentQuestionIndex < _questions.length - 1) {
      setState(() {
        _currentQuestionIndex++;
        _selectedAnswerIndex = null;
        _answerChecked = false;
      });
    } else {
      // Submit score before showing completion dialog
      await _submitScore();
      
      if (!mounted) return;
      
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => AlertDialog(
          title: const Text('Quiz Completed!'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('You scored $_score out of ${_questions.length}.'),
              if (_isSubmitting)
                const Padding(
                  padding: EdgeInsets.only(top: 16.0),
                  child: CircularProgressIndicator(),
                ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(context); // Close dialog
                Navigator.pop(context, {'score': _score}); // Return score
              },
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    // ... rest of your existing build method and widget code ...
  }
} 