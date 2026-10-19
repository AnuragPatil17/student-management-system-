/**
 * Faculty Attendance Marking & Management JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  initAttendanceCounters();
  initAttendanceToggles();
  initMarkAllPresent();
  initDuplicateCheck();
});

/**
 * Update real-time counts of Present, Absent, and Late
 */
function updateSummaryCounts() {
  const presentInputs = document.querySelectorAll('.att-status-input[value="Present"]');
  const absentInputs = document.querySelectorAll('.att-status-input[value="Absent"]');
  const lateInputs = document.querySelectorAll('.att-status-input[value="Late"]');

  const presentBadge = document.getElementById('countPresent');
  const absentBadge = document.getElementById('countAbsent');
  const lateBadge = document.getElementById('countLate');
  const totalBadge = document.getElementById('countTotal');

  if (presentBadge) presentBadge.textContent = presentInputs.length;
  if (absentBadge) absentBadge.textContent = absentInputs.length;
  if (lateBadge) lateBadge.textContent = lateInputs.length;
  if (totalBadge) totalBadge.textContent = (presentInputs.length + absentInputs.length + lateInputs.length);
}

function initAttendanceCounters() {
  updateSummaryCounts();
}

/**
 * Handle interactive P, A, L toggle buttons for each student
 */
function initAttendanceToggles() {
  const toggleButtons = document.querySelectorAll('.att-option-btn');

  toggleButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const studentId = btn.getAttribute('data-student-id');
      const status = btn.getAttribute('data-status');
      const hiddenInput = document.getElementById(`status_input_${studentId}`);

      if (!hiddenInput) return;

      hiddenInput.value = status;

      // Reset peer button active classes for this student
      const peerButtons = document.querySelectorAll(`.att-option-btn[data-student-id="${studentId}"]`);
      peerButtons.forEach(b => {
        b.classList.remove('selected-p', 'selected-a', 'selected-l');
      });

      // Apply appropriate selected class
      if (status === 'Present') btn.classList.add('selected-p');
      if (status === 'Absent') btn.classList.add('selected-a');
      if (status === 'Late') btn.classList.add('selected-l');

      updateSummaryCounts();
    });
  });
}

/**
 * "Mark All Present" shortcut button
 */
function initMarkAllPresent() {
  const markAllBtn = document.getElementById('markAllPresentBtn');
  if (!markAllBtn) return;

  markAllBtn.addEventListener('click', () => {
    const presentBtns = document.querySelectorAll('.att-option-btn[data-status="Present"]');
    presentBtns.forEach(btn => btn.click());
    showToast('All students marked Present.', 'success');
  });
}

/**
 * Duplicate Attendance Check:
 * When faculty changes Subject or Date on the attendance page, check if records already exist.
 */
function initDuplicateCheck() {
  const subjectSelect = document.getElementById('selectSubject');
  const dateInput = document.getElementById('selectDate');
  const classSelect = document.getElementById('selectClass');
  const warningBox = document.getElementById('duplicateWarningBox');

  if (!subjectSelect || !dateInput || !warningBox) return;

  function checkExisting() {
    const subjectId = subjectSelect.value;
    const dateVal = dateInput.value;
    const classId = classSelect ? classSelect.value : '';

    if (!subjectId || !dateVal) {
      warningBox.classList.add('d-none');
      return;
    }

    fetch(`/api/faculty/check-duplicate?subject_id=${subjectId}&date=${dateVal}&class_id=${classId}`)
      .then(res => res.json())
      .then(data => {
        if (data.exists) {
          warningBox.classList.remove('d-none');
          warningBox.innerHTML = `
            <div class="alert alert-warning d-flex align-items-center gap-2 mb-3">
              <i class="bi bi-exclamation-triangle-fill fs-5"></i>
              <div>
                <strong>Notice:</strong> Attendance for this subject and date has already been recorded (${data.count} entries).
                Submitting this form will <strong>update and correct</strong> the existing records.
              </div>
            </div>
          `;
          const submitBtn = document.getElementById('saveAttendanceBtn');
          if (submitBtn) submitBtn.innerHTML = '<i class="bi bi-pencil-square"></i> Update Attendance Records';
        } else {
          warningBox.classList.add('d-none');
          const submitBtn = document.getElementById('saveAttendanceBtn');
          if (submitBtn) submitBtn.innerHTML = '<i class="bi bi-check2-circle"></i> Save Attendance Records';
        }
      })
      .catch(err => console.error('Error checking duplicate attendance:', err));
  }

  subjectSelect.addEventListener('change', checkExisting);
  dateInput.addEventListener('change', checkExisting);
  if (classSelect) classSelect.addEventListener('change', checkExisting);
}
