// appointments.js - Scripts for appointment functionality

document.addEventListener('DOMContentLoaded', function() {
    // Elements for appointment slot handling
    const doctorSelect = document.getElementById('doctor-select');
    const appointmentDate = document.getElementById('appointment-date');
    const appointmentTime = document.getElementById('appointment-time');
    const timeSlots = document.getElementById('time-slots');
    
    // Add event listeners for doctor and date selection
    if (doctorSelect && appointmentDate) {
        doctorSelect.addEventListener('change', fetchAvailableSlots);
        appointmentDate.addEventListener('change', fetchAvailableSlots);
    }
    
    // Initialize with default values if both doctor and date are already set
    if (doctorSelect && appointmentDate && doctorSelect.value && appointmentDate.value) {
        fetchAvailableSlots();
    }
    
    // Function to fetch available time slots from the server
    function fetchAvailableSlots() {
        const doctorId = doctorSelect.value;
        const date = appointmentDate.value;
        
        if (!doctorId || !date) {
            timeSlots.innerHTML = '<div class="alert alert-info">Select a doctor and date to view available slots</div>';
            return;
        }
        
        // Show loading indicator
        timeSlots.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';
        
        // Fetch available slots from the server
        fetch(`/api/appointment-slots?doctor_id=${doctorId}&date=${date}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    timeSlots.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                    return;
                }
                
                if (!data.slots || data.slots.length === 0) {
                    timeSlots.innerHTML = '<div class="alert alert-warning">No available time slots for this date.</div>';
                    return;
                }
                
                // Render time slots
                renderTimeSlots(data.slots);
            })
            .catch(error => {
                console.error('Error fetching appointment slots:', error);
                timeSlots.innerHTML = '<div class="alert alert-danger">Error loading available time slots. Please try again.</div>';
            });
    }
    
    // Function to render time slots as buttons
    function renderTimeSlots(slots) {
        timeSlots.innerHTML = '';
        
        slots.forEach(slot => {
            const slotButton = document.createElement('button');
            slotButton.type = 'button';
            slotButton.className = `btn btn-outline-primary time-slot ${slot.available ? '' : 'unavailable'}`;
            slotButton.textContent = slot.time;
            
            if (!slot.available) {
                slotButton.disabled = true;
                slotButton.classList.add('text-muted');
            } else {
                slotButton.addEventListener('click', function() {
                    // Remove selected class from all time slots
                    document.querySelectorAll('.time-slot').forEach(btn => {
                        btn.classList.remove('selected');
                    });
                    
                    // Add selected class to this slot
                    slotButton.classList.add('selected');
                    
                    // Set the time in the input field
                    if (appointmentTime) {
                        appointmentTime.value = slot.time;
                    }
                });
            }
            
            timeSlots.appendChild(slotButton);
        });
    }
});
