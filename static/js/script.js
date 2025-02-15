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
      url: `http://${serverIP}:3000/upload`, // ✅ Gunakan template literal
      method: "POST",
      data: formData,
      contentType: false,
      processData: false,
      success: function (response) {
        console.log(response);
        alert("File berhasil di-upload dan diproses!");
      },
      error: function (error) {
        console.error("Terjadi error saat upload:", error);
        alert("Gagal upload file.");
      },
    });
  });

  function loadExcelFromServer() {
    fetch(`http://${serverIP}:3000/uploads/excel-file/last-update`)
      .then((response) => response.json())
      .then((data) => {
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(data);
          }, 500); // Tambahkan delay agar loading terlihat
        });
      })
      .then((data) => {
        $("#last-update").text(new Date(data.lastModified).toLocaleString());
        return fetch(`http://${serverIP}:3000/uploads/excel-file`);
      })
      .then((response) => response.arrayBuffer())
      .then((buffer) => {
        var data = new Uint8Array(buffer);
        var workbook = XLSX.read(data, { type: "array" });
        var sheet = workbook.Sheets[workbook.SheetNames[0]];
        var jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

        var headerRow = jsonData[0];
        var table = $(".dynamic-table").DataTable();

        // ✅ Perbaikan dalam menambahkan header
        $(".dynamic-table thead").empty().append(`
          <tr>${headerRow
            .map((col) => `<th class="text-center">${col}</th>`)
            .join("")}</tr>
        `);

        // ✅ Update isi tabel tanpa destroy
        table.clear();
        jsonData.slice(1).forEach((row) => {
          var rowData = headerRow.map((_, i) =>
            row[i] !== undefined ? row[i] : ""
          );
          if (rowData.length === headerRow.length) {
            table.row.add(rowData);
          }
        });

        // Redraw the table
        table.draw();
      })
      .catch((error) => console.error("Error reading file: ", error));
  }
  loadExcelFromServer();

  // Sembunyikan tombol reset saat halaman pertama dimuat
  $("#reset-filter").hide();

  $("area").on("click", function (event) {
    event.preventDefault();
    const city = $(this).data("city");
    $("#selected-city").text("Filter Kota: " + city);

    table.column(3).search(city).draw();
    if (city) {
      $("#reset-filter").show();
    }
  });

  $("#reset-filter").on("click", function () {
    $("#selected-city").text("Menampilkan Semua Kota");
    table.column(3).search("").draw(); // Menghapus filter

    // ✅ Perbaikan: gunakan `$(this)`, bukan `$$(this)`
    $(this).hide();
  });

  table.on("draw", function () {
    let filterApplied = table.column(3).search() !== "";
    $("#reset-filter").toggle(filterApplied);
  });

  function checkExistingImages(tab) {
    let imagesDiv = $(`#images-${tab}`); // Pilih container gambar sesuai tab
    let outputDiv = $(`#output-${tab}`); // Pilih container teks sesuai tab

    fetch(`http://${serverIP}:3000/check-existing-images/${tab}`)
      .then((response) => response.json())
      .then((data) => {
        imagesDiv.empty(); // Bersihkan gambar sebelumnya
        outputDiv.empty(); // Bersihkan teks sebelumnya

        // Handle gambar
        if (data.images.length > 0) {
          imagesDiv.show(); // Tampilkan container gambar
          data.images.forEach((img) => {
            imagesDiv.append(
              `<img src="../uploads/${img}" class="img-fluid mb-3">`
            );
          });
        } else {
          imagesDiv.hide(); // Sembunyikan jika tidak ada gambar
        }

        // Handle teks
        if (data.text) {
          // Tampilkan tabel hasil
          outputDiv.html(`<pre>${data.text}</pre>`); // Menampilkan isi file dalam elemen <pre>

          // Pastikan DataTable diinisialisasi ulang dengan benar
          if ($.fn.DataTable.isDataTable(".output_result")) {
            $(".output_result").DataTable().destroy();
          }
          $(".output_result").DataTable({
            scrollX: true,
            autoWidth: false,
          });
          outputDiv.show(); // Tampilkan teks jika ada
        } else {
          outputDiv.hide(); // Sembunyikan jika tidak ada teks
        }
      })
      .catch((error) => console.error("Error checking images:", error));
  }

  // Cek gambar saat halaman pertama dimuat (default tab1)
  checkExistingImages("tab1");

  // Event listener ketika tab diklik
  $(".nav-link").on("click", function () {
    let selectedTab = $(this).attr("id").replace("-tab", ""); // Ambil tab yang diklik
    checkExistingImages(selectedTab); // Panggil fungsi sesuai tab
  });

  $(".load-result-btn").click(function (event) {
    event.preventDefault();
    var tab = $(this).data("tab");
    // $(`#images-${tab}`).hide(); // Sembunyikan container gambar
    var outputDiv = $("#output-" + tab);

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

        // Tampilkan gambar hasil model
        let existingImages = imagesDiv
          .find("img")
          .map(function () {
            return $(this).attr("src");
          })
          .get();

        data.images.forEach((img) => {
          let imgSrc = `../uploads/${img}`;
          if (!existingImages.includes(imgSrc)) {
            imagesDiv.append(`<img src="${imgSrc}" class="img-fluid mb-3">`);
          }
        });

        imagesDiv.show(); // Pastikan container gambar tampil

        // Tampilkan tabel hasil
        outputDiv.html(`<pre>${data.content}</pre>`); // Menampilkan isi file dalam elemen <pre>

        // Pastikan DataTable diinisialisasi ulang dengan benar
        if ($.fn.DataTable.isDataTable(".output_result")) {
          $(".output_result").DataTable().destroy();
        }
        $(".output_result").DataTable({
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
