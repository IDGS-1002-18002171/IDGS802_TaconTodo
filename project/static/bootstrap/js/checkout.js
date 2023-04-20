// This is a public sample test API key.
// Don’t submit any personally identifiable information in requests made with this key.
// Sign in to see your own test API key embedded in code samples.
const stripe = Stripe("pk_test_51MtEODBMu9RgSpPE73uA5jOG7SYLaorW6hU8u4wE1VNN6ERcPu19SiwPtusKsEXzQTYD6IdcOYgx5c1XlkvEufDg00EH0GUDX4");

// The items the customer wants to buy
const items = [{ id: "xl-tshirt" }];

let elements;
let direccion = '';

initialize();
checkStatus();

document
  .querySelector("#payment-form")
  .addEventListener("submit", handleSubmit);

async function initialize() {
  const items = [{ id: "xl-tshirt" }];
  const response = await fetch("/create-payment-intent", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ items })
  });
  const { clientSecret } = await response.json();

  const appearance = {
    theme: 'stripe'
  };
  
  elements = stripe.elements({ appearance, clientSecret });

  const linkAuthenticationElement = elements.create("linkAuthentication");
  linkAuthenticationElement.mount("#link-authentication-element");

  linkAuthenticationElement.on('change', (event) => {
    emailAddress = event.value.email;
  });

  const paymentElementOptions = {
    layout: "tabs",
  };

  const paymentElement = elements.create("payment", paymentElementOptions);
  paymentElement.mount("#payment-element");
}

async function handleSubmit(e) {
  const address = document.querySelector('#address').value;
  e.preventDefault();
  setLoading(true);
  
  // Envía la dirección del usuario al servicio externo
  const response = await fetch('/update-direccion', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ direccion: address })
  });

  // Si la solicitud fue exitosa, continúa con el pago
  if (response.ok) {
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: {
        // Make sure to change this to your payment completion page
        return_url: "http://localhost:5000/thanks",
        receipt_email: emailAddress
      },
    });

    // Este punto solo se alcanzará si hay un error inmediato al
    // confirmar el pago. De lo contrario, el cliente será redirigido a
    // la `return_url`.
    if (error.type === "card_error" || error.type === "validation_error") {
      showMessage(error.message);
    } else if (error.type === "api_error") {
      showMessage("An error occurred while processing your payment. Please try again later.");
    } else {
      showMessage("An unexpected error occurred.");
    }
  } else {
    showMessage('Error al enviar la dirección del usuario');
  }

  setLoading(false);
}

async function checkStatus() {
  const clientSecret = new URLSearchParams(window.location.search).get(
    "payment_intent_client_secret"
  );

  if (!clientSecret) {
    return;
  }

  const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

  switch (paymentIntent.status) {
    case "succeeded":
      showMessage("Payment succeeded!");
      break;
    case "processing":
      showMessage("Your payment is processing.");
      break;
    case "requires_payment_method":
      showMessage("Your payment was not successful, please try again.");
      break;
    default:
      showMessage("Something went wrong.");
      break;
  }
}

function set_address(address) {
  direccion = address;
}

function showMessage(messageText) {
  const messageContainer = document.querySelector("#payment-message");

  messageContainer.classList.remove("hidden");
  messageContainer.textContent = messageText;

  setTimeout(function () {
    messageContainer.classList.add("hidden");
    messageText.textContent = "";
  }, 4000);
}

function setLoading(isLoading) {
  if (isLoading) {
    document.querySelector("#submit").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
  } else {
    document.querySelector("#submit").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  }
}
