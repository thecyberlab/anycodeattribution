#!/bin/bash

# Function to display menu
display_menu() {
    echo "Select an option:"
    echo "1. Run Abazari Script"
    echo "2. Run Zaffar Script"
    echo "3. Run Ding Script"
    echo "4. Run Kothari Script"
    echo "5. Run Caliskan Script"
    echo "6. Exit"
}

# Function to run selected script
run_script() {
    local script_choice="$1"
    local dir_path="$2"

    home_path=$(dirname "$dir_path")

    case $script_choice in
        1)
            dest_dir="$home_path/abazari_results"
            echo "$dest_dir"

            if [ ! -d "$dest_dir" ]; then
              mkdir -p "$dest_dir"
              echo "Created new directory: $dest_dir"
            else
              echo "Directory already exists: $dest_dir"
            fi

            cp -r "$dir_path"/* "$dest_dir"/
            echo "##################################################################"
            echo "Processing Abazari features"
            ./scripts/run_all_abazari.sh "$dest_dir"
            feature1="abazari"
            echo "##################################################################"
            ;;
        2)
            dest_dir="$home_path/zaffar_results"
            echo "$dest_dir"

            if [ ! -d "$dest_dir" ]; then
              mkdir -p "$dest_dir"
              echo "Created new directory: $dest_dir"
            else
              echo "Directory already exists: $dest_dir"
            fi

            cp -r "$dir_path"/* "$dest_dir"/
            echo "##################################################################"
            echo "Processing Zaffar features"
            ./scripts/run_all_zaffar.sh "$dest_dir"
            feature2="zaffar"
            echo "##################################################################"
            ;;
        3)
            dest_dir="$home_path/ding_results"
            echo "$dest_dir"

            if [ ! -d "$dest_dir" ]; then
              mkdir -p "$dest_dir"
              echo "Created new directory: $dest_dir"
            else
              echo "Directory already exists: $dest_dir"
            fi

            cp -r "$dir_path"/* "$dest_dir"/
            echo "##################################################################"
            echo "Processing Ding features"
            ./scripts/run_all_ding.sh "$dest_dir"
            feature3="ding"
            echo "##################################################################"
            ;;
        4)
            dest_dir="$home_path/kothari_results"
            echo "$dest_dir"

            if [ ! -d "$dest_dir" ]; then
              mkdir -p "$dest_dir"
              echo "Created new directory: $dest_dir"
            else
              echo "Directory already exists: $dest_dir"
            fi

            cp -r "$dir_path"/* "$dest_dir"/
            echo "##################################################################"
            echo "Processing Kothari features"
            ./scripts/run_all_kothari.sh "$dest_dir"
            feature4="kothari"
            ;;
        5)
            dest_dir="$home_path/caliskan_results"
            echo "$dest_dir"

            if [ ! -d "$dest_dir" ]; then
              mkdir -p "$dest_dir"
              echo "Created new directory: $dest_dir"
            else
              echo "Directory already exists: $dest_dir"
            fi

            cp -r "$dir_path"/* "$dest_dir"/
            echo "##################################################################"
            echo "Processing Caliskan features"
            ./scripts/run_all_caliskan.sh "$dest_dir"
            feature5="caliskan"
            echo "##################################################################"
            ;;
    esac
}

display_menu

read -p "Enter your choices separated by spaces (e.g., '1 2 3'): " choices
IFS=" " read -ra choice_array <<< "$choices"

read -p "Enter input to pass to the scripts: " dir_path

echo $dir_path
for choice in "${choice_array[@]}"; do
    if [ "$choice" -eq 6 ]; then
        echo "Exiting..."
        exit 0
    fi
    echo
    run_script "$choice" "$dir_path"
done

./scripts/run_ml_script.sh "$dir_path" "$feature1" "$feature2" "$feature3" "$feature4" "$feature5"