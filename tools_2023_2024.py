import pandas as pd
import numpy as np
from utilities import import_2024_results, import_2023_results
from agents import function_tool
from typing import Optional

# Load data once at module level
df_2023 = import_2023_results()
df_2024 = import_2024_results()
# Default reference for any remaining legacy code
df = df_2024

@function_tool
def get_benchmark_performance(year: int = 2024, assessment_type: str = 'endline', grade_filter: Optional[str] = None):
    """
    Calculate percentage of children above benchmark for specified assessment.
    
    Args:
        assessment_type: 'baseline', 'midline', or 'endline'
        grade_filter: None for all grades, 'Grade R' for Grade R, 'Grade 1' for Grade 1
    
    Returns:
        Dictionary with benchmark analysis
    """
    
    if year == 2023:
        df = df_2023.copy()
    elif year == 2024:
        df = df_2024.copy()
    else:
        return {"error": "Year not found"}
    
    # Define benchmarks
    benchmarks = {'Grade R': 20, 'Grade 1': 40}
    
    # Filter by grade if specified
    if grade_filter:
        df_filtered = df[df['Grade'] == grade_filter].copy()
    else:
        df_filtered = df.copy()
    
    # Get the appropriate EGRA column
    egra_col = f'EGRA {assessment_type.title()}'
    
    if egra_col not in df_filtered.columns:
        return {"error": f"Column {egra_col} not found"}
    
    results = {}
    
    if grade_filter:
        # Single grade analysis - fix the benchmark lookup
        benchmark = benchmarks.get(grade_filter, 20)  # Use full grade name
        scores = df_filtered[egra_col].dropna()
        above_benchmark = (scores >= benchmark).sum()
        total_students = len(scores)
        percentage = (above_benchmark / total_students * 100) if total_students > 0 else 0
        
        results = {
            'grade': grade_filter,
            'assessment': assessment_type,
            'benchmark': benchmark,
            'students_above_benchmark': above_benchmark,
            'total_students': total_students,
            'percentage_above_benchmark': round(percentage, 1),
            'average_score': round(scores.mean(), 1) if len(scores) > 0 else 0
        }
    else:
        # All grades analysis
        for grade_name, benchmark_score in benchmarks.items():
            grade_data = df_filtered[df_filtered['Grade'] == grade_name]
            if len(grade_data) > 0:
                scores = grade_data[egra_col].dropna()
                above_benchmark = (scores >= benchmark_score).sum()
                total_students = len(scores)
                percentage = (above_benchmark / total_students * 100) if total_students > 0 else 0
                
                grade_key = grade_name.replace(' ', '_').lower()  # 'grade_r', 'grade_1'
                results[grade_key] = {
                    'benchmark': benchmark_score,
                    'students_above_benchmark': above_benchmark,
                    'total_students': total_students,
                    'percentage_above_benchmark': round(percentage, 1),
                    'average_score': round(scores.mean(), 1) if len(scores) > 0 else 0
                }
        
        # Overall summary
        all_scores = df_filtered[egra_col].dropna()
        results['overall'] = {
            'total_students': len(all_scores),
            'average_score': round(all_scores.mean(), 1) if len(all_scores) > 0 else 0
        }
    
    return results

@function_tool
def calculate_improvement(year: int = 2024, start_assessment: str = 'baseline', end_assessment: str = 'endline'):
    """
    Calculate improvement from one assessment to another.
    
    Args:
        year: 2023 or 2024
        start_assessment: 'baseline', 'midline', or 'endline'
        end_assessment: 'baseline', 'midline', or 'endline'
    
    Returns:
        Dictionary with improvement analysis
    """
    # Load appropriate dataset based on year
    if year == 2023:
        data_df = df_2023.copy()
    elif year == 2024:
        data_df = df_2024.copy()
    else:
        return {"error": "Year not found"}
    
    start_col = f'EGRA {start_assessment.title()}'
    end_col = f'EGRA {end_assessment.title()}'
    
    if start_col not in data_df.columns or end_col not in data_df.columns:
        return {"error": f"Required columns not found: {start_col}, {end_col}"}
    
    # Filter students with both scores
    df_clean = data_df[[start_col, end_col, 'Grade']].dropna()
    
    if len(df_clean) == 0:
        return {"error": "No students with both assessment scores"}
    
    # Calculate improvement
    df_clean['improvement'] = df_clean[end_col] - df_clean[start_col]
    
    # Categorize students
    improved = (df_clean['improvement'] > 0).sum()
    declined = (df_clean['improvement'] < 0).sum()
    stayed_same = (df_clean['improvement'] == 0).sum()
    
    results = {
        'assessment_period': f"{start_assessment} to {end_assessment}",
        'total_students': len(df_clean),
        'students_improved': improved,
        'students_declined': declined,
        'students_stayed_same': stayed_same,
        'percent_improved': round(improved / len(df_clean) * 100, 1),
        'average_improvement': round(df_clean['improvement'].mean(), 1),
        'median_improvement': round(df_clean['improvement'].median(), 1)
    }
    
    # Grade-level breakdown - fix to match actual grade values
    benchmarks = {'Grade R': 20, 'Grade 1': 40}
    for grade_name in benchmarks.keys():
        grade_data = df_clean[df_clean['Grade'] == grade_name]
        if len(grade_data) > 0:
            grade_improved = (grade_data['improvement'] > 0).sum()
            grade_key = grade_name.replace(' ', '_').lower()
            results[grade_key] = {
                'students': len(grade_data),
                'improved': grade_improved,
                'percent_improved': round(grade_improved / len(grade_data) * 100, 1),
                'average_improvement': round(grade_data['improvement'].mean(), 1)
            }
    
    return results

@function_tool
def get_performance_breakdown(year: int = 2024, breakdown_by: str = 'School', assessment_type: str = 'endline'):
    """
    Get performance breakdown by specified category.
    
    Args:
        year: 2023 or 2024
        breakdown_by: 'School', 'Grade', 'Gender', or 'Group'
        assessment_type: 'baseline', 'midline', or 'endline'
    
    Returns:
        Dictionary with performance breakdown
    """
    # Load appropriate dataset based on year
    if year == 2023:
        data_df = df_2023.copy()
    elif year == 2024:
        data_df = df_2024.copy()
    else:
        return {"error": "Year not found"}
        
    egra_col = f'EGRA {assessment_type.title()}'
    
    if egra_col not in data_df.columns or breakdown_by not in data_df.columns:
        return {"error": f"Required columns not found: {egra_col}, {breakdown_by}"}
    
    # Filter out missing data
    df_clean = data_df[[breakdown_by, egra_col, 'Grade']].dropna()
    
    if len(df_clean) == 0:
        return {"error": "No valid data found"}
    
    results = {
        'breakdown_by': breakdown_by,
        'assessment': assessment_type,
        'categories': {}
    }
    
    benchmarks = {'Grade R': 20, 'Grade 1': 40}
    
    for category in df_clean[breakdown_by].unique():
        category_data = df_clean[df_clean[breakdown_by] == category]
        
        category_results = {
            'total_students': len(category_data),
            'average_score': round(category_data[egra_col].mean(), 1),
            'median_score': round(category_data[egra_col].median(), 1),
            'grades': {}
        }
        
        # Breakdown by grade within category
        for grade_name, benchmark_score in benchmarks.items():
            grade_data = category_data[category_data['Grade'] == grade_name]
            if len(grade_data) > 0:
                scores = grade_data[egra_col]
                above_benchmark = (scores >= benchmark_score).sum()
                
                grade_key = grade_name.replace(' ', '_').lower()
                category_results['grades'][grade_key] = {
                    'students': len(grade_data),
                    'average_score': round(scores.mean(), 1),
                    'above_benchmark': above_benchmark,
                    'percent_above_benchmark': round(above_benchmark / len(grade_data) * 100, 1)
                }
        
        results['categories'][str(category)] = category_results
    
    return results

@function_tool
def identify_students_needing_support(year: int = 2024, assessment_type: str = 'endline', bottom_percentile: int = 25):
    """
    Identify students who need the most support based on low scores.
    
    Args:
        year: 2023 or 2024
        assessment_type: 'baseline', 'midline', or 'endline'
        bottom_percentile: Percentile threshold for identifying low performers
    
    Returns:
        Dictionary with list of students needing support
    """
    # Load appropriate dataset based on year
    if year == 2023:
        data_df = df_2023.copy()
    elif year == 2024:
        data_df = df_2024.copy()
    else:
        return {"error": "Year not found"}
        
    egra_col = f'EGRA {assessment_type.title()}'
    
    if egra_col not in data_df.columns:
        return {"error": f"Column {egra_col} not found"}
    
    # Required columns for student identification
    required_cols = ['Mcode', 'School', 'Name', 'Grade', egra_col]
    missing_cols = [col for col in required_cols if col not in data_df.columns]
    
    if missing_cols:
        return {"error": f"Missing required columns: {missing_cols}"}
    
    df_clean = data_df[required_cols].dropna()
    
    if len(df_clean) == 0:
        return {"error": "No valid student data found"}
    
    # Calculate percentile threshold
    threshold_score = np.percentile(df_clean[egra_col], bottom_percentile)
    
    # Identify students below threshold
    students_needing_support = df_clean[df_clean[egra_col] <= threshold_score]
    
    results = {
        'assessment': assessment_type,
        'threshold_percentile': bottom_percentile,
        'threshold_score': round(threshold_score, 1),
        'total_students_identified': len(students_needing_support),
        'students': []
    }
    
    # Format student information - fix benchmark lookup
    benchmarks = {'Grade R': 20, 'Grade 1': 40}
    for _, student in students_needing_support.iterrows():
        benchmark = benchmarks.get(student['Grade'], 20)
        student_info = {
            'mcode': student['Mcode'],
            'name': student['Name'],
            'school': student['School'],
            'grade': student['Grade'],
            'score': student[egra_col],
            'gap_to_benchmark': max(0, benchmark - student[egra_col])
        }
        results['students'].append(student_info)
    
    # Sort by score (lowest first)
    results['students'].sort(key=lambda x: x['score'])
    
    return results

@function_tool
def get_summary_statistics(year: int = 2024):
    """
    Get overall summary statistics for all assessments.
    
    Args:
        year: 2023 or 2024
    
    Returns:
        Dictionary with comprehensive summary
    """
    # Load appropriate dataset based on year
    if year == 2023:
        data_df = df_2023.copy()
    elif year == 2024:
        data_df = df_2024.copy()
    else:
        return {"error": "Year not found"}
        
    assessment_cols = ['EGRA Baseline', 'EGRA Midline', 'EGRA Endline']
    available_assessments = [col for col in assessment_cols if col in data_df.columns]
    
    if not available_assessments:
        return {"error": "No EGRA assessment columns found"}
    
    results = {
        'total_students': len(data_df),
        'schools': data_df['School'].nunique() if 'School' in data_df.columns else 0,
        'grade_distribution': data_df['Grade'].value_counts().to_dict() if 'Grade' in data_df.columns else {},
        'assessments': {}
    }
    
    for col in available_assessments:
        assessment_name = col.replace('EGRA ', '').lower()
        scores = data_df[col].dropna()
        
        if len(scores) > 0:
            results['assessments'][assessment_name] = {
                'students_assessed': len(scores),
                'average_score': round(scores.mean(), 1),
                'median_score': round(scores.median(), 1),
                'min_score': scores.min(),
                'max_score': scores.max(),
                'std_deviation': round(scores.std(), 1)
            }
    
    return results

@function_tool
def analyze_program_effectiveness(year: int = 2024):
    """Comprehensive program effectiveness analysis"""
    baseline_bench = get_benchmark_performance(year, 'baseline')
    endline_bench = get_benchmark_performance(year, 'endline')
    improvement = calculate_improvement(year)
    
    return {
        'baseline_performance': baseline_bench,
        'endline_performance': endline_bench,
        'improvement_analysis': improvement
    }
    
@function_tool
def school_comparison_report(year: int = 2024):
    """Compare performance across schools"""
    return get_performance_breakdown(year, 'School', 'endline')

# Optional: Add a function to get available data info for the agent
@function_tool
def get_data_info(year: int = 2024):
    """Get information about the available data for the agent to understand what it's working with"""
    # Load appropriate dataset based on year
    if year == 2023:
        data_df = df_2023.copy()
    elif year == 2024:
        data_df = df_2024.copy()
    else:
        return {"error": "Year not found"}
        
    return {
        'total_records': len(data_df),
        'columns': list(data_df.columns),
        'schools': sorted(data_df['School'].unique().tolist()) if 'School' in data_df.columns else [],
        'grades': sorted(data_df['Grade'].unique().tolist()) if 'Grade' in data_df.columns else [],
        'sample_data': data_df.head(3).to_dict('records') if len(data_df) > 0 else []
    }

# Wrapper functions for 2023-specific calls (for the 2023 agent)
@function_tool
def get_benchmark_performance_2023(assessment_type: str = 'endline', grade_filter: Optional[str] = None):
    """2023-specific benchmark performance analysis"""
    return get_benchmark_performance(2023, assessment_type, grade_filter)

@function_tool
def calculate_improvement_2023(start_assessment: str = 'baseline', end_assessment: str = 'endline'):
    """2023-specific improvement analysis"""
    return calculate_improvement(2023, start_assessment, end_assessment)

@function_tool
def get_performance_breakdown_2023(breakdown_by: str = 'School', assessment_type: str = 'endline'):
    """2023-specific performance breakdown"""
    return get_performance_breakdown(2023, breakdown_by, assessment_type)

@function_tool
def identify_students_needing_support_2023(assessment_type: str = 'endline', bottom_percentile: int = 25):
    """2023-specific student support identification"""
    return identify_students_needing_support(2023, assessment_type, bottom_percentile)

@function_tool
def get_summary_statistics_2023():
    """2023-specific summary statistics"""
    return get_summary_statistics(2023)

@function_tool
def analyze_program_effectiveness_2023():
    """2023-specific program effectiveness analysis"""
    return analyze_program_effectiveness(2023)

@function_tool
def school_comparison_report_2023():
    """2023-specific school comparison"""
    return school_comparison_report(2023)

@function_tool
def get_data_info_2023():
    """2023-specific data information"""
    return get_data_info(2023)

# Wrapper functions for 2024-specific calls (for the 2024 agent)
@function_tool
def get_benchmark_performance_2024(assessment_type: str = 'endline', grade_filter: Optional[str] = None):
    """2024-specific benchmark performance analysis"""
    return get_benchmark_performance(2024, assessment_type, grade_filter)

@function_tool
def calculate_improvement_2024(start_assessment: str = 'baseline', end_assessment: str = 'endline'):
    """2024-specific improvement analysis"""
    return calculate_improvement(2024, start_assessment, end_assessment)

@function_tool
def get_performance_breakdown_2024(breakdown_by: str = 'School', assessment_type: str = 'endline'):
    """2024-specific performance breakdown"""
    return get_performance_breakdown(2024, breakdown_by, assessment_type)

@function_tool
def identify_students_needing_support_2024(assessment_type: str = 'endline', bottom_percentile: int = 25):
    """2024-specific student support identification"""
    return identify_students_needing_support(2024, assessment_type, bottom_percentile)

@function_tool
def get_summary_statistics_2024():
    """2024-specific summary statistics"""
    return get_summary_statistics(2024)

@function_tool
def analyze_program_effectiveness_2024():
    """2024-specific program effectiveness analysis"""
    return analyze_program_effectiveness(2024)

@function_tool
def school_comparison_report_2024():
    """2024-specific school comparison"""
    return school_comparison_report(2024)

@function_tool
def get_data_info_2024():
    """2024-specific data information"""
    return get_data_info(2024)