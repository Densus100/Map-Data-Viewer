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

  function loadModelTable(tab) {
    // console.log("loadModelTable");

    var model = false;

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    }

    $(`#load-${model}-table`).click(function (event) {
      event.preventDefault();
      let fileUrl = `http://${serverIP}:3000/uploads/${model}_model/${model}_output.csv`; // Adjust file path if needed
      let tableContainer = $(`#${model}_output_container`); // This is where the table will be created

      // console.log(`Loading CSV: ${fileUrl}`);

      // Show loading spinner
      tableContainer.html(`
            <p class="text-center">Loading data...<br>
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </p>
        `);

      // Fetch CSV file and process it
      fetch(fileUrl)
        .then(response => response.arrayBuffer()) // Read as binary buffer
        .then(buffer => {
          let data = new Uint8Array(buffer);
          let workbook = XLSX.read(data, { type: "array" });
          let sheet = workbook.Sheets[workbook.SheetNames[0]];
          let jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 });

          let headerRow = jsonData[0]; // Extract header row

          // ✅ Create the table dynamically inside the container
          tableContainer.html(`
                    <table id="${model}_output" class="display output_result_tab2" style="width:100%">
                        <thead>
                            <tr>${headerRow.map(col => `<th class="text-center">${col}</th>`).join("")}</tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                `);

          let table = $(`#${model}_output`).DataTable({
            scrollX: true,
            autoWidth: false,
          }); // Initialize DataTable

          // ✅ Insert table rows
          jsonData.slice(1).forEach(row => {
            let rowData = headerRow.map((_, i) => row[i] !== undefined ? row[i] : "");
            if (rowData.length === headerRow.length) {
              table.row.add(rowData);
            }
          });

          // ✅ Redraw the table
          table.draw();

          // ✅ Remove the loading spinner
          tableContainer.find(".spinner-border").remove();
        })
        .catch(error => {
          console.error("Error loading CSV:", error);
          tableContainer.html("<p class='text-danger'>Failed to load CSV.</p>");
        });
    });
  }


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

    var model = false;

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    }

    // 🔍 Check if images & content are already present
    let hasImages = imagesDiv.find("img").length > 0;
    let hasText = outputDiv.text().trim().length > 0;

    if (hasImages && hasText) {
      console.log(`Skipping fetch for ${tab}: Content already loaded.`);
      return; // ✅ Stop fetching if content exists
    }

    // 🔄 Show loading spinner while fetching
    outputDiv.html(`
      <p class="text-center">Loading content...<br>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </p>
    `);

    outputDiv.css("display", "inline");

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
              `<img src="http://${serverIP}:3000/uploads/${img}" class="img-fluid mb-3">`
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
          if ($.fn.DataTable.isDataTable(`.output_result_${tab}`)) {
            $(`.output_result_${tab}`).DataTable().destroy();
          }
          $(`.output_result_${tab}`).DataTable({
            scrollX: true,
            // autoWidth: false,
          });
          outputDiv.show(); // Tampilkan teks jika ada
        } else {
          outputDiv.hide(); // Sembunyikan jika tidak ada teks
        }

        if (data.text) {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/${model}_model/${model}_output.csv`;
          $(`#${model}-download-link`).attr("href", modelDownloadLink);
          loadModelTable(tab);
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

    var model = false;

    if (tab == "tab1") {
      model = "kmeans";
    } else if (tab == "tab2") {
      model = "gmm";
    } else if (tab == "tab3") {
      model = "hierarchical";
    }

    // $(`#images-${tab}`).hide(); // Sembunyikan container gambar
    let imagesDiv = $(`#images-${tab}`);
    imagesDiv.empty();
    var outputDiv = $(`#output-${tab}`);

    // Show loading animation FIRST before fetching data
    outputDiv.html(`
      <p class="text-center">Generating data...<br>
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </p>
    `);
    outputDiv.css("display", "inline");

    // Delay the fetch slightly to ensure the spinner is rendered first
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
          let imgSrc = `http://${serverIP}:3000/uploads/${img}`;
          if (!existingImages.includes(imgSrc)) {
            imagesDiv.append(`<img src="${imgSrc}" class="img-fluid mb-3">`);
          }
        });

        imagesDiv.show(); // Pastikan container gambar tampil

        // Tampilkan tabel hasil
        outputDiv.html(`<pre>${data.content}</pre>`); // Menampilkan isi file dalam elemen <pre>

        // Pastikan DataTable diinisialisasi ulang dengan benar
        if ($.fn.DataTable.isDataTable(`.output_result_${tab}`)) {
          $(`.output_result_${tab}`).DataTable().destroy();
        }
        $(`.output_result_${tab}`).DataTable({
          scrollX: true,
          // autoWidth: false,
        });

        outputDiv.show();

        if (data.content) {
          let modelDownloadLink = `http://${serverIP}:3000/uploads/${model}_model/${model}_output.csv`;
          $(`#${model}-download-link`).attr("href", modelDownloadLink);
          loadModelTable(tab);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        outputDiv.html("<p class='text-danger'>Failed to load data.</p>");
      });
  });

  setTimeout(() => {
    $("#loading-overlay").fadeOut("slow"); // Hide spinner after the page is ready
  }, 1000); // Adjust time as needed

});
