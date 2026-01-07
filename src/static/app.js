document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");
  const skillsEmailInput = document.getElementById("skills-email");
  const viewSkillsBtn = document.getElementById("view-skills-btn");
  const skillsList = document.getElementById("skills-list");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;
        
        // Build skills HTML if skills exist
        let skillsHTML = "";
        if (details.skills && details.skills.length > 0) {
          skillsHTML = `<p><strong>Skills you'll gain:</strong> ${details.skills.join(", ")}</p>`;
        }

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${skillsHTML}
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Handle view skills button
  viewSkillsBtn.addEventListener("click", async () => {
    const email = skillsEmailInput.value;
    
    if (!email) {
      skillsList.innerHTML = '<p class="error">Please enter an email address</p>';
      skillsList.classList.remove("hidden");
      return;
    }

    try {
      const response = await fetch(`/skills/${encodeURIComponent(email)}`);
      const result = await response.json();

      if (response.ok) {
        if (result.skills.length === 0) {
          skillsList.innerHTML = '<p class="info">No skills gained yet. Sign up for activities to gain skills!</p>';
        } else {
          // Create skills list safely using DOM methods to prevent XSS
          const ul = document.createElement('ul');
          ul.className = 'skills-list';
          result.skills.forEach(skill => {
            const li = document.createElement('li');
            li.textContent = skill; // Use textContent to prevent XSS
            ul.appendChild(li);
          });
          skillsList.innerHTML = '';
          skillsList.appendChild(ul);
        }
        skillsList.classList.remove("hidden");
      } else if (response.status === 400) {
        skillsList.innerHTML = '<p class="error">Invalid email format. Please enter a valid email address.</p>';
        skillsList.classList.remove("hidden");
      } else {
        skillsList.innerHTML = '<p class="error">Failed to load skills. Please try again.</p>';
        skillsList.classList.remove("hidden");
      }
    } catch (error) {
      skillsList.innerHTML = '<p class="error">Network error. Please check your connection and try again.</p>';
      skillsList.classList.remove("hidden");
      console.error("Error fetching skills:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
