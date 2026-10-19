/**
 * Student Dashboard & Attendance Analytics JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initStudentCharts();
});

/**
 * Initializes Student Attendance Gauge/Doughnut and Subject Bar Chart
 */
function initStudentCharts() {
  const overallCanvas = document.getElementById('studentOverallChart');
  const subjectCanvas = document.getElementById('studentSubjectChart');

  if (!overallCanvas && !subjectCanvas) return;

  fetch('/api/student/chart-data')
    .then(res => res.json())
    .then(data => {
      // 1. Overall Attendance Doughnut Chart
      if (overallCanvas && data.overall) {
        const percentage = data.overall.percentage;
        const attended = data.overall.attended;
        const absent = data.overall.absent;
        const late = data.overall.late;

        // Color coding: Green if >= 75%, Red warning if < 75%
        const isHealthy = percentage >= 75;
        const primaryColor = isHealthy ? '#10b981' : '#ef4444';

        new Chart(overallCanvas, {
          type: 'doughnut',
          data: {
            labels: ['Attended (Present)', 'Absent', 'Late'],
            datasets: [{
              data: [attended, absent, late],
              backgroundColor: [primaryColor, '#fca5a5', '#fcd34d'],
              borderWidth: 2,
              borderColor: '#ffffff'
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '74%',
            plugins: {
              legend: { position: 'bottom', labels: { boxWidth: 12, padding: 12, font: { family: 'Outfit' } } },
              tooltip: {
                callbacks: {
                  label: function(context) {
                    return ` ${context.label}: ${context.raw} lectures`;
                  }
                }
              }
            }
          }
        });
      }

      // 2. Subject-Wise Attendance Breakdown (Bar Chart)
      if (subjectCanvas && data.subjects) {
        new Chart(subjectCanvas, {
          type: 'bar',
          data: {
            labels: data.subjects.names,
            datasets: [{
              label: 'Attendance %',
              data: data.subjects.percentages,
              backgroundColor: data.subjects.percentages.map(pct => pct >= 75 ? '#2563eb' : '#ef4444'),
              borderRadius: 6
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
              y: {
                min: 0,
                max: 100,
                ticks: { callback: v => v + '%' },
                grid: { color: '#f1f5f9' }
              },
              x: { grid: { display: false } }
            },
            plugins: {
              legend: { display: false }
            }
          }
        });
      }
    })
    .catch(err => console.error('Error loading student chart data:', err));
}
