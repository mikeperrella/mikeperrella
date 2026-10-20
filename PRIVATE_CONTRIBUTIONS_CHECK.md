# Private GitHub contribution checklist (local / not part of profile README)

Your profile ZIP's `data/contributions.json` reports **257** publicly visible contributions for 2025-10-19 to 2026-10-20. The GitHub public calendar endpoint also reported **257** on 2026-10-20. That does **not** prove every private commit has been credited.

1. On your GitHub profile, choose **Contribution settings → Private contributions** to display anonymized activity publicly. Verify you're looking at the last year rather than a different selected year.
2. Open **one private repository** with missing activity locally in Cursor. Run the following *read-only* commands in that repo, not in `mikeperrella/mikeperrella`:

   ```powershell
   git log -10 --format="%h | %an <%ae> | %as"
   git branch -a
   git remote -v
   git log origin/HEAD --since="1 year ago" --format="%ae" | Sort-Object -Unique
   ```

   Compare the **author** email to your GitHub-recognized noreply address (it is valid). Confirm the missing commits are on the default branch or `gh-pages`, rather than remaining on an unmerged feature branch.
3. Also check that the repository is not a fork, the work was pushed to GitHub, and the dates fall in the selected period. GitHub can take up to 24 hours to update eligible activity.
4. **Do not amend, rebase, force-push, or fabricate commits** to change the green squares. If everything qualifies and activity stays missing after 24 hours, contact GitHub Support with a few affected commit URLs.

GitHub documentation:
- https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions
- https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements

Note: We removed the unused `scripts/contrib.json` fallback from the contribution generator because the uploaded copy was not the correct user's data. Never substitute those historical values for your own.
