function goNext() {
  $(".carousel").carousel("next");
}

function goBack() {
  $(".carousel").carousel("prev");
}

async function makePrediction() {
  const data_hora = $("#startDate").val();
  const categoria = $("#inputGroupSelect01").val();
  const feriado = Number($("#exampleCheck1").is(":checked"));

  $.post(
    "./api/knn/rat",
    {
      data_hora,
      categoria,
      feriado,
    },
    function (data, status) {
      alert("Data: " + data + "\nStatus: " + status);
    }
  );
}

$("form").on("submit", async function (e) {
  e.preventDefault();
  makePrediction();
});

$(function () {
  $(".carousel").carousel({
    interval: false,
  });
});
