import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://192.168.1.5:8000'; // Update this with your backend URL

  // Get stored token
  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token'); // Changed from 'token' to 'access_token'
  }

  // Fetch questions from API
  static Future<List<dynamic>> fetchQuestions(String endpoint) async {
    try {
      final token = await getToken();
      final headers = {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

      final response = await http.get(
        Uri.parse('$baseUrl$endpoint'),
        headers: headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Failed to load questions: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error: $e');
    }
  }

  // Submit aptitude score
  static Future<Map<String, dynamic>?> submitAptitudeScore(int score, String category) async {
    try {
      final token = await getToken();
      if (token == null) {
        throw Exception('No authentication token found. Please login again.');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/api/submit-aptitude-score/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: json.encode({
          'score': score,
          'category': category,
        }),
      );

      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else if (response.statusCode == 401) {
        throw Exception('Authentication failed. Please login again.');
      } else {
        throw Exception('Failed to submit score: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error submitting score: $e');
    }
  }

  // Login method
  static Future<Map<String, dynamic>> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/login/'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'email': email,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        // Store access token
        if (data['access'] != null) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.setString('access_token', data['access']);
          if (data['refresh'] != null) {
            await prefs.setString('refresh_token', data['refresh']);
          }
        }
        return data;
      } else {
        throw Exception('Login failed: ${response.body}');
      }
    } catch (e) {
      throw Exception('Error during login: $e');
    }
  }

  // Logout method
  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }
} 