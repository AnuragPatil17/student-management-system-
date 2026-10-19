/**
 * Admin Dashboard & Management JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initAdminCharts();
  initStudentFilter();
});

/**
 * Initializes Chart.js charts on the Admin Dashboard
 */
function initAdminCharts() {
  const trendCanvas = document.getElementById('attendanceTrendChart');
  const deptCanvas = document.getElementById('deptAttendanceChart');
  const statusCanvas = document.getElementById('statusRatioChart');

  // Fetch chart data from API
  if (trendCanvas || deptCanvas || statusCanvas) {
    fetch('/api/admin/chart-data')
      .then(response => response.json())
      .then(data => {
        // 1. 7-Day Attendance Trend Chart (Line)
        if (trendCanvas && data.trend) {
          new Chart(trendCanvas, {
            type: 'line',
            data: {
              labels: data.trend.dates,
              datasets: [{
                label: 'Present Students',
                data: data.trend.present,
                borderColor: '#10b981',
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                fill: true,
                tension: 0.35,
                borderWidth: 2.5,
                pointRadius: 4,
                pointBackgroundColor: '#10b981'
              }, {
                label: 'Absent Students',
                data: data.trend.absent,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.08)',
                fill: true,
                tension: 0.35,
                borderWidth: 2,
                pointRadius: 4,
                pointBackgroundColor: '#ef4444'
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { position: 'top', labels: { boxWidth: 12, font: { family: 'Outfit' } } }
              },
              scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
              }
            }
          });
        }

        // 2. Department-wise Attendance Comparison (Bar)
        if (deptCanvas && data.departments) {
          new Chart(deptCanvas, {
            type: 'bar',
            data: {
              labels: data.departments.names,
              datasets: [{
                label: 'Attendance Rate (%)',
                data: data.departments.rates,
                backgroundColor: ['#2563eb', '#3b82f6', '#06b6d4', '#6366f1'],
                borderRadius: 6
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false }
              },
              scales: {
                y: { min: 0, max: 100, ticks: { callback: v => v + '%' } },
                x: { grid: { display: false } }
              }
            }
          });
        }

        // 3. Status Ratio Doughnut Chart
        if (statusCanvas && data.status_ratio) {
          new Chart(statusCanvas, {
            type: 'doughnut',
            data: {
              labels: ['Present', 'Absent', 'Late'],
              datasets: [{
                data: [data.status_ratio.present, data.status_ratio.absent, data.status_ratio.late],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                borderWidth: 2,
                borderColor: '#ffffff'
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              cutout: '70%',
              plugins: {
                legend: { position: 'bottom', labels: { boxWidth: 12, padding: 14 } }
              }
            }
          });
        }
      })
      .catch(err => console.error('Error loading admin chart data:', err));
  }
}

/**
 * Filter students table dynamically by search input or department dropdown
 */
function initStudentFilter() {
  const searchInput = document.getElementById('studentSearchInput');
  const deptFilter = document.getElementById('studentDeptFilter');
  const table = document.getElementById('studentsTable');

  if (!table) return;
  const rows = table.querySelectorAll('tbody tr');

  function applyFilters() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const dept = deptFilter ? deptFilter.value.toLowerCase().trim() : '';

    rows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const rowDept = row.getAttribute('data-dept')?.toLowerCase() || '';

      const matchesQuery = !query || text.includes(query);
      const matchesDept = !dept || rowDept === dept;

      if (matchesQuery && matchesDept) {
        row.style.display = '';
      } else {
        row.style.display = 'none';
      }
    });
  }

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (deptFilter) deptFilter.addEventListener('change', applyFilters);
}

/**
 * Populate Edit Student Modal
 */
function editStudent(id, name, roll, email, deptId, classId, semester, phone) {
  const form = document.getElementById('editStudentForm');
  if (!form) return;
  form.action = `/admin/students/edit/${id}`;
  
  document.getElementById('edit_student_name').value = name;
  document.getElementById('edit_student_roll').value = roll;
  document.getElementById('edit_student_email').value = email;
  document.getElementById('edit_student_dept').value = deptId;
  document.getElementById('edit_student_class').value = classId;
  document.getElementById('edit_student_semester').value = semester;
  document.getElementById('edit_student_phone').value = phone || '';

  const modal = new bootstrap.Modal(document.getElementById('editStudentModal'));
  modal.show();
}

/**
 * Populate Edit Faculty Modal
 */
function editFaculty(id, name, code, email, deptId, designation, phone) {
  const form = document.getElementById('editFacultyForm');
  if (!form) return;
  form.action = `/admin/faculty/edit/${id}`;

  document.getElementById('edit_faculty_name').value = name;
  document.getElementById('edit_faculty_code').value = code;
  document.getElementById('edit_faculty_email').value = email;
  document.getElementById('edit_faculty_dept').value = deptId;
  document.getElementById('edit_faculty_designation').value = designation;
  document.getElementById('edit_faculty_phone').value = phone || '';

  const modal = new bootstrap.Modal(document.getElementById('editFacultyModal'));
  modal.show();
}
