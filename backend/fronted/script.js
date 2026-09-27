document.addEventListener('DOMContentLoaded', function() {
  // Form submission event listener
  document.getElementById('uploadForm').addEventListener('submit', async function(e) {
    e.preventDefault();

    // Show loader and clear previous messages
    document.getElementById('loading').style.display = 'block';
    document.getElementById('resultMessage').innerText = '';

    const fileInput = document.getElementById('csvFile');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
      // Send the file to the backend using fetch API
      const response = await fetch('/predict', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      console.log("Response data:", data);
      
      // Hide loader after receiving response
      document.getElementById('loading').style.display = 'none';
      
      if (data.error) {
        document.getElementById('resultMessage').innerText = data.error;
      } else {
        // Display the result message
        document.getElementById('resultMessage').innerText = data.result_message;
        
        // Render flux chart if flux data is available
        if (data.flux_data) {
          renderFluxChart(data.flux_data);
        }
      }
    } catch (error) {
      document.getElementById('loading').style.display = 'none';
      document.getElementById('resultMessage').innerText = 'An error occurred: ' + error;
    }
  });

  // Function to render the flux data as a line chart using Chart.js
  function renderFluxChart(fluxData) {
    const ctx = document.getElementById('fluxChart').getContext('2d');
    // Destroy previous chart instance if exists
    if (window.fluxChartInstance) {
      window.fluxChartInstance.destroy();
    }
    window.fluxChartInstance = new Chart(ctx, {
      type: 'line',
      data: {
        labels: fluxData.map((_, index) => index + 1),
        datasets: [{
          label: 'Flux Values',
          data: fluxData,
          borderColor: '#1f77b4',
          fill: false,
          tension: 0.1,
          pointRadius: 0
        }]
      },
      options: {
        responsive: true,
        scales: {
          x: {
            title: {
              display: true,
              text: 'Time Step'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Flux Value'
            }
          }
        },
        plugins: {
          tooltip: {
            mode: 'index'
          }
        }
      }
    });
  }
});
