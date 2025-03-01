document.addEventListener("DOMContentLoaded", function() {
    const allDaysCheckbox = document.querySelector("#id_all_days");
    const dayCheckboxes = document.querySelectorAll(
        "#id_monday, #id_tuesday, #id_wednesday, #id_thursday, #id_friday, #id_saturday, #id_sunday"
    );

    function updateAllDaysCheckbox() {
        let allChecked = Array.from(dayCheckboxes).every(checkbox => checkbox.checked);
        allDaysCheckbox.checked = allChecked;
    }

    allDaysCheckbox.addEventListener("change", function() {
        dayCheckboxes.forEach(checkbox => {
            checkbox.checked = allDaysCheckbox.checked;
        });
    });

    dayCheckboxes.forEach(checkbox => {
        checkbox.addEventListener("change", function() {
            updateAllDaysCheckbox();
        });
    });
});
