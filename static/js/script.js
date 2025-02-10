$(document).ready(function () {
  var table = $(".dynamic-table").DataTable();
  $("table").DataTable();

  // Use browser's IP for the request (this assumes you are using the correct network)
  var serverIP = window.location.hostname; // This will dynamically fetch the IP of the server

  $("#file-upload-btn").click(function () {
    $("#file-upload").click();
  });

  $("#file-upload").change(function (event) {
    var file = event.target.files[0];
    if (!file) return;

    var formData = new FormData();
    formData.append("file", file);

    $.ajax({
      url: `http://${serverIP}:3000/upload`,  // Use dynamic IP
      method: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        console.log(response);
        alert("File berhasil di-upload dan di-replace!");
      },
      error: function (error) {
        console.error("Terjadi error saat upload:", error);
        alert("Gagal upload file.");
      },
    });
  });

  // $("#load-data-btn").click(function () {
  loadExcelFromServer();
  // });

  function loadExcelFromServer() {
    var serverIP = window.location.hostname;

    fetch(`http://${serverIP}:3000/uploads/excel-file/last-update`)
      .then((response) => response.json())
      .then((data) => {
        document.getElementById("last-update").innerText = new Date(
          data.lastModified
        ).toLocaleString();

        return fetch(`http://${serverIP}:3000/uploads/excel-file`).then(
          (response) => response.arrayBuffer()
        );
      })
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];

        // Hancurkan DataTable jika sudah ada
        if ($.fn.DataTable.isDataTable(".dynamic-table")) {
          $(".dynamic-table").DataTable().destroy();
        }

        // Bersihkan tabel sebelum mengisi ulang
        $(".dynamic-table thead").empty();
        $(".dynamic-table tbody").empty();

        // Tambahkan header
        var tableHeadHtml = "<tr>";
        headerRow.forEach(function (col) {
          tableHeadHtml += '<th class="text-center">' + col + "</th>";
        });
        tableHeadHtml += "</tr>";
        $(".dynamic-table thead").html(tableHeadHtml);

        var tableBodyHtml = "";
        jsonData.slice(1).forEach(function (row) {
          tableBodyHtml += "<tr>";
          headerRow.forEach(function (_, i) {
            tableBodyHtml += `<td>${row[i] !== undefined ? row[i] : ""}</td>`;
          });
          tableBodyHtml += "</tr>";
        });

        $(".dynamic-table tbody").html(tableBodyHtml);

        // Inisialisasi ulang DataTable dengan scroll horizontal
        $(".dynamic-table").DataTable({
          scrollX: true,
          autoWidth: false,
        });
      })
      .catch((error) => console.error("Error reading file: ", error));
  }

  $("area").on("click", function (event) {
    event.preventDefault();
    const city = $(this).data("city");

    table.column(4).search(city).draw();
  });

  $(".load-result-btn").click(function () {
    var tab = $(this).data("tab"); // Ambil tab yang diklik
    var outputDiv = $("#output-" + tab); // Target output berdasarkan tab

    fetch(`http://${serverIP}:3000/load-content/${tab}`)
      .then((response) => response.text())
      .then((data) => {
        outputDiv.html(`<pre>${data}</pre>`); // Menampilkan isi file dalam elemen pre agar rapi
      })
      .catch((error) => {
        console.error("Error:", error);
        outputDiv.html("<p class='text-danger'>Failed to load data.</p>");
      });
  });
});
