$(document).ready(function() {
    $('#form').submit(function(e) {
        e.preventDefault();
        $('.error').html('');

        var firstname = $('#fullname').val();
        var lastname = $('#lastname').val();
        var email = $('#email').val();
        var phonenumber = $('#phonenumber').val();
        var password = $('#password').val();
        var confirm_password = $('#confirm_password').val();

        // Define validation rules here
        var isValid = true;

        if (firstname === '') {
            isValid = false;
            $('#fullname').next('.error').html('Full Name is required.');
        }

        if (lastname === '') {
            isValid = false;
            $('#lastname').next('.error').html('Last Name is required.');
        }

        if (email === '') {
            isValid = false;
            $('#email').next('.error').html('Email is required.');
        } else if (!isValidEmail(email)) {
            isValid = false;
            $('#email').next('.error').html('Invalid email format.');
        }

        if (phonenumber === '') {
            isValid = false;
            $('#phonenumber').next('.error').html('Phone Number is required.');
        } else if (!isValidPhoneNumber(phonenumber)) {
            isValid = false;
            $('#phonenumber').next('.error').html('Invalid phone number format. Please enter 10 digits.');
        }

        if (password === '') {
            isValid = false;
            $('#password').next('.error').html('Password is required.');
        } else if (!isValidPassword(password)) {
            isValid = false;
            $('#password').next('.error').html('Give a proper password.');
        }

        if (confirm_password === '') {
            isValid = false;
            $('#confirm_password').next('.error').html('Confirm Password is required.');
        } else if (password !== confirm_password) {
            isValid = false;
            $('#confirm_password').next('.error').html('Passwords do not match.');
        }

        if (isValid) {
            // Form is valid, you can submit the data or take further actions here
            $('#form')[0].submit();
        }
    });

    function isValidEmail(email) {
        // You can implement a regular expression for email validation here.
        // For a simple example, you can use the following regex:
        var emailRegex = /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$/;
        return emailRegex.test(email);
    }

    function isValidPhoneNumber(phone) {
        // Use a regular expression to check for exactly 10 digits
        var phoneRegex = /^\d{10}$/;
        return phoneRegex.test(phone);
    }

    function isValidPassword(password) {
        // Use a regular expression to check for a high-secure password
        var passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
        return passwordRegex.test(password);
    }
});





