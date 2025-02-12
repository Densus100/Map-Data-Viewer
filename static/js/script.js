$(document).ready(function () {
  var table = $(".dynamic-table").DataTable({
    scrollX: true, // Mengaktifkan scroll horizontal
    autoWidth: false, // Mencegah lebar kolom menjadi tidak proporsional
  });

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
      url: `http://${serverIP}:3000/upload`, // Use dynamic IP
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
        const lastUpdateDate = data.lastModified; // lastupdate

        // Display the last update date in the HTML
        document.getElementById("last-update").innerText = new Date(
          lastUpdateDate
        ).toLocaleString();

        // get file excel
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
        var tableHeadHtml = "<tr>";
        headerRow.forEach(function (col) {
          tableHeadHtml += '<th class="text-center">' + col + "</th>";
        });
        tableHeadHtml += "</tr>";

        $(".dynamic-table thead").html(tableHeadHtml);

        table.clear();

        // Add data rows
        jsonData.slice(1).forEach(function (row) {
          var rowData = [];
          headerRow.forEach(function (_, i) {
            rowData.push(row[i] !== undefined ? row[i] : "");
          });

          if (rowData.length === headerRow.length) {
            table.row.add(rowData);
          }
        });

        // Redraw the table
        table.draw();
      })
      .catch((error) => console.error("Error reading file: ", error));
  }

  $("area").on("click", function (event) {
    event.preventDefault();
    const city = $(this).data("city");
    $("#selected-city").text("Filter Kota: " + city);

    table.column(4).search(city).draw();
  });

  $(".load-result-btn").click(function () {
    var tab = $(this).data("tab"); // Ambil tab yang diklik
    var outputDiv = $("#output-" + tab); // Target output berdasarkan tab
    var imagesDiv = $("#images-" + tab); // Div untuk menampilkan gambar

    // Tampilkan loading animation
    outputDiv.html(`<p class="text-center">Generating data...<br>
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </p>`);

    fetch(`http://${serverIP}:3000/load-content/${tab}`)
      .then((response) => response.json()) // Ubah response menjadi JSON
      .then((data) => {
        outputDiv.empty(); // Bersihkan loading
        imagesDiv.empty(); // Bersihkan gambar sebelumnya

        // Tampilkan gambar hasil model
        data.images.forEach((img) => {
          imagesDiv.append(
            `<img src="../uploads/${img}" class="img-fluid mb-3">`
          );
        });

        // Tampilkan tabel hasil
        outputDiv.html(`<pre>${data.content}</pre>`); // Menampilkan isi file dalam elemen <pre>

        // Pastikan DataTable diinisialisasi ulang dengan benar
        if ($.fn.DataTable.isDataTable("table")) {
          $("table").DataTable().destroy();
        }
        $("table").DataTable({
          scrollX: true,
          autoWidth: false,
        });
      })
      .catch((error) => {
        console.error("Error:", error);
        outputDiv.html("<p class='text-danger'>Failed to load data.</p>");
      });
  });
});
