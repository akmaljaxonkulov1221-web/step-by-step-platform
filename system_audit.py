#!/usr/bin/env python3
"""
System Functionality Audit
Checks all existing functions and identifies what needs to be fixed
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def audit_existing_functions():
    """Audit existing system functions"""
    print("=== AUDITING EXISTING SYSTEM FUNCTIONS ===")
    
    try:
        import app
        
        with app.app.app_context():
            audit_results = {}
            
            # 1. Test System
            print("\n1. TESTING TEST SYSTEM")
            test_count = app.Test.query.count()
            question_count = app.Question.query.count()
            test_result_count = app.TestResult.query.count()
            
            audit_results['test_system'] = {
                'total_tests': test_count,
                'total_questions': question_count,
                'total_results': test_result_count,
                'status': 'OK' if test_count > 0 else 'NEEDS_TESTS'
            }
            
            print(f"  Tests: {test_count}, Questions: {question_count}, Results: {test_result_count}")
            
            # 2. Results System
            print("\n2. TESTING RESULTS SYSTEM")
            if test_result_count > 0:
                latest_result = app.TestResult.query.order_by(app.TestResult.id.desc()).first()
                audit_results['results_system'] = {
                    'has_results': True,
                    'latest_result_id': latest_result.id,
                    'status': 'OK'
                }
                print(f"  Latest result ID: {latest_result.id}")
            else:
                audit_results['results_system'] = {
                    'has_results': False,
                    'status': 'NEEDS_RESULTS'
                }
                print("  No results found")
            
            # 3. Certificate System
            print("\n3. TESTING CERTIFICATE SYSTEM")
            cert_count = app.Certificate.query.count()
            audit_results['certificate_system'] = {
                'total_certificates': cert_count,
                'status': 'OK' if cert_count >= 0 else 'ERROR'
            }
            print(f"  Certificates: {cert_count}")
            
            # 4. Scoring System
            print("\n4. TESTING SCORING SYSTEM")
            try:
                # Test scoring functions
                daily_points = app.calculate_daily_points(80)
                dtm_points = app.calculate_dtm_points(1, 10)
                
                audit_results['scoring_system'] = {
                    'daily_points_function': 'OK',
                    'dtm_points_function': 'OK',
                    'status': 'OK'
                }
                print(f"  Daily points (80%): {daily_points}, DTM points (1st): {dtm_points}")
            except Exception as e:
                audit_results['scoring_system'] = {
                    'status': f'ERROR: {str(e)}'
                }
                print(f"  Scoring error: {e}")
            
            # 5. Topics System
            print("\n5. TESTING TOPICS SYSTEM")
            subject_count = app.Subject.query.count()
            topic_count = app.Topic.query.count()
            
            audit_results['topics_system'] = {
                'total_subjects': subject_count,
                'total_topics': topic_count,
                'status': 'OK' if subject_count > 0 else 'NEEDS_SUBJECTS'
            }
            print(f"  Subjects: {subject_count}, Topics: {topic_count}")
            
            # 6. User System
            print("\n6. TESTING USER SYSTEM")
            user_count = app.User.query.count()
            admin_count = app.User.query.filter_by(is_admin=True).count()
            student_count = app.User.query.filter_by(is_admin=False, is_group_leader=False).count()
            
            audit_results['user_system'] = {
                'total_users': user_count,
                'admin_users': admin_count,
                'student_users': student_count,
                'status': 'OK' if user_count > 0 else 'NEEDS_USERS'
            }
            print(f"  Users: {user_count} (Admin: {admin_count}, Students: {student_count})")
            
            # 7. Group System
            print("\n7. TESTING GROUP SYSTEM")
            group_count = app.Group.query.count()
            
            audit_results['group_system'] = {
                'total_groups': group_count,
                'status': 'OK' if group_count > 0 else 'NEEDS_GROUPS'
            }
            print(f"  Groups: {group_count}")
            
            return audit_results
            
    except Exception as e:
        print(f"Audit error: {e}")
        return {'status': f'ERROR: {str(e)}'}

def check_database_schema():
    """Check database schema for new features"""
    print("\n=== CHECKING DATABASE SCHEMA ===")
    
    try:
        import app
        
        with app.app.app_context():
            # Check if we need to add new columns/tables
            schema_status = {}
            
            # Check Topic model for new fields
            try:
                sample_topic = app.Topic.query.first()
                if sample_topic:
                    schema_status['topic_model'] = {
                        'youtube_link': hasattr(sample_topic, 'youtube_link'),
                        'pdf_file': hasattr(sample_topic, 'pdf_file'),
                        'description': hasattr(sample_topic, 'description'),
                        'status': 'OK'
                    }
                else:
                    schema_status['topic_model'] = {
                        'status': 'NO_TOPICS_FOUND'
                    }
            except Exception as e:
                schema_status['topic_model'] = {
                    'status': f'ERROR: {str(e)}'
                }
            
            # Check if we need AI chat table
            schema_status['ai_chat_table'] = {
                'exists': hasattr(app, 'AIChat') if 'AIChat' in dir(app) else False,
                'status': 'NEEDS_CREATION'
            }
            
            # Check if we need enhanced certificate table
            schema_status['enhanced_certificate'] = {
                'needs_upgrade': True,
                'status': 'NEEDS_ENHANCEMENT'
            }
            
            return schema_status
            
    except Exception as e:
        print(f"Schema check error: {e}")
        return {'status': f'ERROR: {str(e)}'}

def check_routes():
    """Check existing routes"""
    print("\n=== CHECKING ROUTES ===")
    
    try:
        import app
        
        routes = []
        for rule in app.app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'rule': str(rule)
            })
        
        # Check for required routes
        required_routes = [
            'admin_dashboard',
            'student_dashboard',
            'register',
            'login',
            'logout',
            'subjects',
            'tests',
            'test_results'
        ]
        
        existing_endpoints = [route['endpoint'] for route in routes]
        missing_routes = [route for route in required_routes if route not in existing_endpoints]
        
        route_status = {
            'total_routes': len(routes),
            'missing_routes': missing_routes,
            'status': 'OK' if len(missing_routes) == 0 else 'MISSING_ROUTES'
        }
        
        print(f"  Total routes: {len(routes)}")
        if missing_routes:
            print(f"  Missing routes: {missing_routes}")
        else:
            print("  All required routes exist")
        
        return route_status
        
    except Exception as e:
        print(f"Route check error: {e}")
        return {'status': f'ERROR: {str(e)}'}

def generate_audit_report():
    """Generate comprehensive audit report"""
    print("STEP BY STEP EDUCATION PLATFORM - SYSTEM AUDIT")
    print("Auditing all system functions...")
    
    audit_results = {
        'timestamp': datetime.now().isoformat(),
        'audit': {}
    }
    
    # Run audits
    audit_results['audit']['existing_functions'] = audit_existing_functions()
    audit_results['audit']['database_schema'] = check_database_schema()
    audit_results['audit']['routes'] = check_routes()
    
    # Determine overall status
    all_status = []
    for category, results in audit_results['audit'].items():
        if isinstance(results, dict) and 'status' in results:
            all_status.append(results['status'])
        elif isinstance(results, dict):
            for key, value in results.items():
                if isinstance(value, dict) and 'status' in value:
                    all_status.append(value['status'])
    
    error_count = len([s for s in all_status if 'ERROR' in s or 'NEEDS' in s])
    
    audit_results['summary'] = {
        'total_categories': len(audit_results['audit']),
        'issues_found': error_count,
        'overall_status': 'OK' if error_count == 0 else 'NEEDS_FIXES'
    }
    
    # Save report
    with open('system_audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== AUDIT SUMMARY ===")
    print(f"Categories checked: {audit_results['summary']['total_categories']}")
    print(f"Issues found: {audit_results['summary']['issues_found']}")
    print(f"Overall status: {audit_results['summary']['overall_status']}")
    print(f"Report saved: system_audit_report.json")
    
    return audit_results

def main():
    """Main audit function"""
    report = generate_audit_report()
    
    if report['summary']['overall_status'] == 'OK':
        print("\nAll systems operational!")
        return True
    else:
        print(f"\nFound {report['summary']['issues_found']} issues that need fixing.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
