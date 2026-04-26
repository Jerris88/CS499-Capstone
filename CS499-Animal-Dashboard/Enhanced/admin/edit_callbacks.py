from dash import Input, Output, State, no_update
import pandas as pd


# registers callbacks for editing and deleting records
def register_edit_callbacks(app, shelter):

    # ======================
    # STORE SELECTED RECORD ID
    # ======================
    @app.callback(
        Output("selected-animal-id", "data"),
        Input("admin-datatable-id", "derived_virtual_data"),
        Input("admin-datatable-id", "derived_virtual_selected_rows"),
        prevent_initial_call=True,
    )
    def store_selected_animal_id(rows, selected_rows):
        if not rows or not selected_rows:
            return None

        selected_index = selected_rows[0]

        if selected_index >= len(rows):
            return None

        selected_record = rows[selected_index]
        return selected_record.get("animal_id")

    # ======================
    # REFRESH ADMIN TABLE
    # ======================
    @app.callback(
        Output("admin-datatable-id", "data"),
        Input("btn-update", "n_clicks"),
        Input("confirm-delete-dialog", "submit_n_clicks"),
        prevent_initial_call=False,
    )
    def refresh_admin_table(update_clicks, delete_clicks):
        records = shelter.read({})
        df = pd.DataFrame(records)

        # Mongo id does not display cleanly in the admin table
        if not df.empty and "_id" in df.columns:
            df = df.drop(columns=["_id"])

        return df.to_dict("records")

    # ======================
    # UPDATE SELECTED ROW
    # ======================
    @app.callback(
        Output("edit-output", "children"),
        Output("edit-output", "className"),
        Input("btn-update", "n_clicks"),
        State("selected-animal-id", "data"),
        State("admin-datatable-id", "derived_virtual_data"),
        State("admin-datatable-id", "derived_virtual_selected_rows"),
        prevent_initial_call=True,
    )
    def update_selected_row(n_clicks, original_animal_id, rows, selected_rows):
        if not n_clicks:
            return no_update

        if not original_animal_id:
            return "Please select a row to update.", "admin-message error"

        if not rows or not selected_rows:
            return "Please select a row to update.", "admin-message error"

        selected_index = selected_rows[0]

        if selected_index >= len(rows):
            return "Selected row is invalid.", "admin-message error"

        selected_record = rows[selected_index]

        # remove Mongo id before sending updated values back to database
        update_data = {
            key: value
            for key, value in selected_record.items()
            if key != "_id"
        }

        updated_count = shelter.update(
            {"animal_id": original_animal_id},
            update_data,
        )

        if updated_count > 0:
            return (
                f"Record {original_animal_id} updated successfully.",
                "admin-message success",
            )

        return "No records were updated.", "admin-message error"

    # ======================
    # SHOW DELETE CONFIRMATION
    # ======================
    @app.callback(
        Output("confirm-delete-dialog", "displayed"),
        Input("btn-delete", "n_clicks"),
        prevent_initial_call=True,
    )
    def show_delete_confirm(n_clicks):
        if n_clicks:
            return True

        return False

    # ======================
    # DELETE SELECTED ROW
    # ======================
    @app.callback(
        Output("edit-output", "children", allow_duplicate=True),
        Output("edit-output", "className", allow_duplicate=True),
        Input("confirm-delete-dialog", "submit_n_clicks"),
        State("selected-animal-id", "data"),
        prevent_initial_call=True,
    )
    def delete_selected_row(confirm_clicks, original_animal_id):
        if not confirm_clicks:
            return no_update

        if not original_animal_id:
            return "Please select a row to delete.", "admin-message error"

        deleted_count = shelter.delete({"animal_id": original_animal_id})

        if deleted_count > 0:
            return (
                f"Record {original_animal_id} deleted successfully.",
                "admin-message success",
            )

        return "No records were deleted.", "admin-message error"

    # ======================
    # ENABLE / DISABLE BUTTONS
    # ======================
    @app.callback(
        Output("btn-update", "disabled"),
        Output("btn-delete", "disabled"),
        Input("admin-datatable-id", "derived_virtual_selected_rows"),
    )
    def toggle_buttons(selected_rows):
        if not selected_rows:
            return True, True

        return False, False